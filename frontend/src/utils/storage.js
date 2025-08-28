// filepath: d:\project\hcchat\frontend\src\utils\storage.js
// 用户信息存储工具
export function saveUserInfo(userInfo) {
    localStorage.setItem('userInfo', JSON.stringify(userInfo));
}

export function getUserInfo() {
    const userInfo = localStorage.getItem('userInfo');
    return userInfo ? JSON.parse(userInfo) : null;
}

export function clearUserInfo() {
    localStorage.removeItem('userInfo');
}

// 为了向后兼容，保留邀请码相关函数
export function saveInviteCode(code) {
    localStorage.setItem('inviteCode', code);
}

export function getInviteCode() {
    return localStorage.getItem('inviteCode');
}

export function clearInviteCode() {
    localStorage.removeItem('inviteCode');
}