from django.core.mail import send_mail

def send_post_recommendation_email(post, cd, post_url):
    subject = f"{cd['name']} ({cd['email']}) recommends you read {post.title}"
    message = (
        f"Read {post.title} at {post_url}\n\n"
        f"{cd['name']}\'s comments: {cd['comments']}"
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=[cd['to']]
    )