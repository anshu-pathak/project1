from itsdangerous import URLSafeTimedSerializer

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer('14be1971fc014f1b84')
    return serializer.dumps(email, salt='f495b66803a6512d')


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer('14be1971fc014f1b84')
    try:
        email = serializer.loads(
            token,
            salt='f495b66803a6512d',
            max_age=expiration
        )
    except:
        return False
    return email