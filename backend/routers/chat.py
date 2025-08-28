from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Message
from typing import List, Optional
from datetime import datetime
import os
import uuid
import shutil
from pathlib import Path

router = APIRouter()

# 文件上传配置
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_FILE_TYPES = {"text/plain", "application/pdf", "application/msword", 
                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                     "application/vnd.ms-excel", 
                     "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}

# 创建上传目录
os.makedirs(UPLOAD_DIR, exist_ok=True)

class SendMessageRequest(BaseModel):
    user_id: int
    content: str
    target_user_id: Optional[int] = None  # 管理员发消息给指定用户

class MessageResponse(BaseModel):
    id: int
    username: str
    content: str
    message_type: str = 'text'
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    is_from_admin: bool
    timestamp: datetime
    is_deleted: bool
    can_delete: bool = False  # 是否可以删除

    model_config = {"from_attributes": True}

class ChatHistoryResponse(BaseModel):
    messages: List[MessageResponse]
    total_count: int

class DeleteMessageRequest(BaseModel):
    user_id: int
    message_id: int

class DeleteMessageResponse(BaseModel):
    message: str

class SendMessageResponse(BaseModel):
    message: str
    message_id: int

@router.post("/upload_file", response_model=SendMessageResponse)
async def upload_file(
    user_id: int = Form(...),
    target_user_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),  # 可选的文字说明
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> SendMessageResponse:
    """上传文件或图片"""
    
    # 验证用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 验证文件大小
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"文件大小超过限制 ({MAX_FILE_SIZE // (1024*1024)}MB)")
    
    # 验证文件类型
    allowed_types = ALLOWED_IMAGE_TYPES | ALLOWED_FILE_TYPES
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    # 确定消息类型
    message_type = "image" if file.content_type in ALLOWED_IMAGE_TYPES else "file"
    
    # 生成唯一文件名
    file_extension = Path(file.filename).suffix if file.filename else ""
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    try:
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 创建消息记录
        if description and description.strip():
            # 如果有文字说明，格式为：[FILE/IMAGE] 文件名 - 说明内容
            content = f"[{message_type.upper()}] {file.filename} - {description.strip()}" if file.filename else f"[{message_type.upper()}] 文件 - {description.strip()}"
        else:
            # 如果没有说明，只显示文件信息
            content = f"[{message_type.upper()}] {file.filename}" if file.filename else f"[{message_type.upper()}] 文件"
        
        new_message = Message(
            user_id=user_id,
            content=content,
            message_type=message_type,
            file_path=file_path,
            file_name=file.filename,
            file_size=file.size,
            is_from_admin=bool(user.is_admin),
            target_user_id=target_user_id if bool(user.is_admin) else None
        )
        
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        
        return SendMessageResponse(
            message=f"{message_type}上传成功",
            message_id=getattr(new_message, "id")
        )
        
    except Exception as e:
        # 如果保存失败，删除已上传的文件
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@router.get("/download/{message_id}")
async def download_file(message_id: int, db: Session = Depends(get_db)):
    """下载文件"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")
    
    file_path = getattr(message, "file_path")
    file_name = getattr(message, "file_name")
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type='application/octet-stream'
    )

@router.post("/send_message", response_model=SendMessageResponse)
async def send_message(request: SendMessageRequest, db: Session = Depends(get_db)) -> SendMessageResponse:
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 如果是管理员发消息，必须指定目标用户
    if bool(user.is_admin) and not request.target_user_id:
        raise HTTPException(status_code=400, detail="管理员发送消息必须指定目标用户")
    
    # 如果指定了目标用户，验证目标用户存在
    if request.target_user_id:
        target_user = db.query(User).filter(User.id == request.target_user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="目标用户不存在")
    
    new_message = Message(
        user_id=request.user_id,
        content=request.content,
        is_from_admin=bool(user.is_admin),
        target_user_id=request.target_user_id if bool(user.is_admin) else None
    )
    
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    # 使用字典构造，让FastAPI自动序列化
    return SendMessageResponse(
        message="消息发送成功",
        message_id=getattr(new_message, "id")  # 使用实例属性而不是Column对象
    )

@router.get("/chat_history/{user_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    user_id: int, 
    target_user_id: Optional[int] = Query(None), 
    db: Session = Depends(get_db)
) -> ChatHistoryResponse:
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 显式检查is_admin字段
        is_admin = bool(user.is_admin) if hasattr(user, 'is_admin') else False
        
        if is_admin and target_user_id:
            # 管理员查看与特定用户的对话
            # 查询：1) 管理员发给目标用户的消息 2) 目标用户发的普通消息
            admin_messages = db.query(Message).filter(
                (Message.user_id == user_id) & 
                (Message.is_from_admin.is_(True)) & 
                (Message.target_user_id == target_user_id) &
                (Message.is_deleted == False)
            ).all()
            
            user_messages = db.query(Message).filter(
                (Message.user_id == target_user_id) & 
                (Message.is_from_admin.is_(False)) & 
                (Message.is_deleted == False)
            ).all()
            
            # 合并消息并按时间排序
            all_messages = admin_messages + user_messages
            messages = sorted(all_messages, key=lambda x: getattr(x, "timestamp"))
        elif not is_admin:
            # 普通用户看到：1) 自己发的消息 2) 管理员发给自己的消息
            messages = db.query(Message).filter(
                (
                    # 自己发的消息
                    (Message.user_id == user_id) |
                    # 管理员发给自己的消息
                    ((Message.is_from_admin.is_(True)) & (Message.target_user_id == user_id))
                ) & (Message.is_deleted == False)
            ).order_by(Message.timestamp.asc()).all()
        else:
            # 管理员未选择用户，返回空消息列表
            messages = []
        
        # 手动构建响应对象，确保类型正确
        message_responses: List[MessageResponse] = []
        for msg in messages:
            # 获取关联的用户信息
            msg_user = db.query(User).filter(User.id == getattr(msg, "user_id")).first()
            username = msg_user.username if msg_user else "Unknown"
            
            # 判断用户是否可以删除这条消息
            can_delete = False
            if is_admin:
                # 管理员可以删除任意消息
                can_delete = True
            elif getattr(msg, "user_id") == user_id:
                # 普通用户可以删除自己的消息（无时间限制）
                can_delete = True
            
            message_responses.append(MessageResponse(
                id=getattr(msg, "id"),
                username=str(username),
                content=str(getattr(msg, "content")),
                message_type=str(getattr(msg, "message_type", "text")),
                file_name=getattr(msg, "file_name"),
                file_size=getattr(msg, "file_size"),
                is_from_admin=bool(getattr(msg, "is_from_admin")),
                timestamp=getattr(msg, "timestamp"),
                is_deleted=bool(getattr(msg, "is_deleted", False)),
                can_delete=can_delete
            ))
        
        return ChatHistoryResponse(
            messages=message_responses,
            total_count=len(message_responses)
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取聊天记录错误: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

class UserResponse(BaseModel):
    id: int
    username: str
    invite_code: str
    is_admin: bool
    is_online: bool
    created_at: datetime

    model_config = {"from_attributes": True}

@router.post("/delete_message", response_model=DeleteMessageResponse)
async def delete_message(request: DeleteMessageRequest, db: Session = Depends(get_db)) -> DeleteMessageResponse:
    from datetime import datetime, timezone
    
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    message = db.query(Message).filter(Message.id == request.message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")
    
    if getattr(message, "is_deleted", False):
        raise HTTPException(status_code=400, detail="消息已被删除")
    
    # 检查删除权限
    can_delete = False
    if bool(user.is_admin):
        # 管理员可以删除任意消息
        can_delete = True
    elif getattr(message, "user_id") == request.user_id:
        # 普通用户可以删除自己的消息（无时间限制）
        can_delete = True
    
    if not can_delete:
        raise HTTPException(status_code=403, detail="无权限删除此消息")
    
    # 标记消息为已删除
    setattr(message, "is_deleted", True)
    setattr(message, "deleted_at", datetime.now(timezone.utc))
    setattr(message, "deleted_by", request.user_id)
    
    db.commit()
    
    return DeleteMessageResponse(message="消息删除成功")

@router.get("/users", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)) -> List[UserResponse]:
    """获取所有用户列表"""
    users = db.query(User).all()  # 返回所有用户
    user_responses: List[UserResponse] = []
    for user in users:
        user_responses.append(UserResponse(
            id=getattr(user, "id"),
            username=str(user.username),
            invite_code=str(user.invite_code),
            is_admin=bool(user.is_admin),
            is_online=bool(user.is_online),
            created_at=getattr(user, "created_at")
        ))
    return user_responses