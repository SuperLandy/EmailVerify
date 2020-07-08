from django.conf import settings
from django.db import models
# django密码转换
from django.contrib.auth.hashers import make_password
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
import uuid


# Create your models here.

class Users(models.Model):
    id = models.UUIDField(max_length=128, null=False, default=uuid.uuid1(), primary_key=True)
    nickname = models.CharField(max_length=16, null=False, blank=False, unique=True)
    email = models.EmailField(max_length=32, null=False, blank=False, unique=True)
    password = models.CharField(max_length=64, null=False, blank=False)
    head = models.ImageField(default="default.png")
    age = models.CharField(max_length=3, blank=True, null=True)
    sex = models.CharField(max_length=2, blank=True, null=True)
    is_active = models.BooleanField(default=False)

    def email_save(self):
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save()

    # 生成token
    def generate_activate_token(self, expires_in=settings.DEFAULT_TOKEN_EXPIRES_IN):
        s = Serializer(settings.SECRET_KEY, expires_in)
        return s.dumps({'id': str(self.id)})

    # token校验
    @staticmethod
    def check_activate_token(token):
        s = Serializer(settings.SECRET_KEY)
        try:
            data = s.loads(token)
        except BadSignature:
            return '无效的激活码'
        except SignatureExpired:
            return '激活码已过期'

        user = Users.objects.filter(id=data.get('id'))[0]
        if not user:
            return '激活的账号不存在'
        if user.is_active:
            return '账号已激活，无需重复点击'
        if not user.is_active:
            user.is_active = True
            user.save()
        return '激活成功'
