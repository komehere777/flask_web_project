from apps.app import db
from apps.crud.models import User
from werkzeug.security import generate_password_hash

# 기존 사용자의 비밀번호를 업데이트하는 스크립트
def update_password_hash():
    users = User.query.all()
    for user in users:
        # 기존 비밀번호를 사용할 수 없기 때문에 새 비밀번호를 설정해야 합니다.
        # 예시로 모든 사용자 비밀번호를 'new_password'로 설정합니다.
        new_password = 'new_password'
        user.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.add(user)
    db.session.commit()

if __name__ == "__main__":
    update_password_hash()
    print("All user passwords have been updated.")
