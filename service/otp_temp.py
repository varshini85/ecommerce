from datetime import datetime

def otp_email_template(
    otp: str,
    purpose: str = "Forget Password",
    brand_name: str = "Lovio",
    expires_minutes: int = 10,
    logo_url: str | None = None
):
    current_year = datetime.now().year

    # optional logo block
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
                <div style="font-size:18px; font-weight:700; margin:0 0 6px;">
                  Your {purpose} code
                </div>
                <div style="font-size:15px; color:#444; margin:0 0 18px;">
                  Use the code below to continue.
                </div>
              </td>
            </tr>

            <tr>
              <td style="padding:0 28px 8px;">
                <div style="
                  font-size:32px; font-weight:800; letter-spacing:4px;
                  padding:16px 20px; display:inline-block; background:#fff;
                  border:2px dashed #c9c9c9; border-radius:8px;">
                  {otp}
                </div>
              </td>
            </tr>

            <tr>
              <td style="padding:4px 28px 28px;">
                <div style="font-size:14px; color:#666; margin-top:8px;">
                  This code expires in {expires_minutes} minutes.
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
