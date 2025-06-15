from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
from ..core.database import get_db
from ..core.security import get_password_hash, verify_password, create_session_token
from ..core.models import User, SignIn, RoleEnum, PasswordResetToken
from .schemas import UserCreate, UserLogin, ForgotPassword, ResetPassword, UserResponse
from ..core.config import settings
import smtplib
from email.mime.text import MIMEText

router = APIRouter()
security = HTTPBearer()

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        role=RoleEnum.admin if user.role == "admin" else RoleEnum.user
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/signin", response_model=dict)
def signin(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    session_token = create_session_token()
    new_signin = SignIn(
        user_id=db_user.id,
        session_token=session_token,
        role=db_user.role
    )
    db.add(new_signin)
    db.commit()
    
    return {
        "message": "Login successful",
        "session_token": session_token,
        "role": db_user.role.value
    }

@router.post("/signout", response_model=dict)
def signout(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    session_token = credentials.credentials
    signin = db.query(SignIn).filter(SignIn.session_token == session_token).first()
    
    if signin:
        signin.is_active = False
        db.commit()
    
    return {"message": "Logged out successfully"}

@router.post("/forgot-password", response_model=dict)
def forgot_password(data: ForgotPassword, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    
    token = secrets.token_urlsafe(32)
    expiration_time = datetime.utcnow() + timedelta(hours=1)
    
    reset_token = db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).first()
    if reset_token:
        reset_token.token = token
        reset_token.expiration_time = expiration_time
        reset_token.used = False
    else:
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expiration_time=expiration_time
        )
        db.add(reset_token)
    db.commit()
    
    try:
        msg = MIMEText(f"Your password reset token is: {token}")
        msg["Subject"] = "Password Reset Request"
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = user.email
        
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.send_message(msg)
    except Exception as e:
        print(f"Error sending email: {e}")
    
    return {"message": "Password reset token sent to your email"}

@router.post("/reset-password", response_model=dict)
def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    reset_token = db.query(PasswordResetToken).filter(PasswordResetToken.token == data.token).first()
    
    if not reset_token or reset_token.used or reset_token.expiration_time < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.hashed_password = get_password_hash(data.new_password)
    reset_token.used = True
    db.commit()
    
    return {"message": "Password reset successfully"}