from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import EmailCode


@shared_task(bind=True, autoretry_for=(Exception,), max_retries=3, retry_backoff=True)
def send_email_code(self, email: str, code: str, purpose: str):
    """
    Фоновая задача: отправить письмо с кодом (активация или сброс).
    Если отправка неудачна (исключение), Celery будет пытаться повторно (до max_retries).
    """
    subject = (
        "Код активации" if purpose == "activation" else "Код восстановления пароля"
    )
    lifespan = (
        settings.ACTIVATION_CODE_EXPIRE_MINUTES
        if purpose == "activation"
        else settings.RESET_CODE_EXPIRE_MINUTES
    )
    message = f"Здравствуйте,\n\nВаш код: {code}\nОн действителен {lifespan} минут."

    from_email = settings.EMAIL_HOST_USER
    # send_mail может выбросить исключение, если SMTP не отвечает — autoretry_for его обрабатывает
    send_mail(subject, message, from_email, [email], fail_silently=False)


@shared_task
def cleanup_expired_codes():
    """
    Периодическая задача, которая удаляет записи EmailCode, срок действия которых истёк.
    Запускается beat’ом по расписанию, не вручную.
    """
    now = timezone.now()
    deleted, _ = EmailCode.objects.filter(expires_at__lt=now).delete()
    # Можно логировать:
    # logger.info(f"cleanup_expired_codes: удалено {deleted} кодов")
