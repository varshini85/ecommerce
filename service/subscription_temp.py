# service/email_templates.py
from datetime import datetime
from typing import Optional

def welcome_email_template(brand_name: str = "Lovio", logo_url: Optional[str] = None):
    current_year = datetime.now().year
    logo_block = (
        f'''<img src="{logo_url}" alt="{brand_name}" width="64" height="64"
               style="display:block;margin:0 auto 8px; border:0; outline:none; text-decoration:none;">'''
        if logo_url else ""
    )
    return f"""<!doctype html>
<html>
  <body style="margin:0; padding:0; background:#f7f7f8; font-family: Arial, Helvetica, sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f7f7f8;">
      <tr>
        <td align="center" style="padding:24px;">
          <table role="presentation" width="640" cellpadding="0" cellspacing="0"
                 style="max-width:640px; width:100%; background:#ffffff; border:1px solid #eee; border-radius:12px;">
            <tr>
              <td style="padding:32px 28px 28px; text-align:center;">
                {logo_block}
                <div style="font-size:28px; line-height:1; font-weight:700; letter-spacing:0.2px; margin:0; color:#111;">
                  {brand_name}
                </div>
              </td>
            </tr>

            <tr>
              <td style="padding:0 28px 6px; color:#111;">
                <div style="font-size:15px; color:#444; margin:0 0 18px;">
                  Thanks for subscribing to {brand_name}. We’ll send occasional updates and offers.
                </div>
              </td>
            </tr>

            <tr>
              <td style="padding:16px 28px 28px; text-align:center;">
                <div style="font-size:12px; color:#999;">© {current_year} {brand_name}</div>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""

def admin_alert_template(
    brand_name: str = "Lovio",
    logo_url: Optional[str] = None,
    subscriber_email: str = "",
):
    current_year = datetime.now().year
    timestamp = datetime.now().strftime("%d %b %Y • %I:%M %p")

    logo_block = (
        f'''<img src="{logo_url}" alt="{brand_name}" width="64" height="64"
               style="display:block;margin:0 auto 8px; border:0; outline:none; text-decoration:none;">'''
        if logo_url else ""
    )

    return f"""<!doctype html>
<html>
  <body style="margin:0; padding:0; background:#f7f7f8; font-family: Arial, Helvetica, sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f7f7f8;">
      <tr>
        <td align="center" style="padding:24px;">
          <table role="presentation" width="640" cellpadding="0" cellspacing="0"
                 style="max-width:640px; width:100%; background:#ffffff; border:1px solid #eee; border-radius:12px;">

            <tr>
              <td style="padding:32px 28px 28px; text-align:center;">
                {logo_block}
                <div style="font-size:28px; line-height:1; font-weight:700; margin:0; color:#111;">
                  {brand_name} — New Subscriber Alert
                </div>
              </td>
            </tr>

            <tr>
              <td style="padding:0 28px 18px; color:#111;">
                <div style="font-size:16px; margin:0 0 12px;">
                  Hello Admin,
                </div>
                <div style="font-size:15px; color:#444; margin:0 0 18px;">
                  A new user has subscribed to {brand_name}.
                </div>

                <div style="font-size:15px; margin:0 0 6px;">
                  <strong>Email:</strong> {subscriber_email}
                </div>
                <div style="font-size:15px; margin:0 0 12px;">
                  <strong>Subscribed At:</strong> {timestamp}
                </div>

              </td>
            </tr>

            <tr>
              <td style="padding:16px 28px 28px; text-align:center;">
                <div style="font-size:12px; color:#999;">© {current_year} {brand_name}</div>
              </td>
            </tr>

          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""
