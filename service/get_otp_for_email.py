import os
import time
from database.user import get_user_details, update_user_details
from utils.generate_otp import generate_otp
from utils.send_mail import send_email
from fastapi import HTTPException
from schema.auth_model import AuthResponseDetails

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

is_default_otp = os.getenv('IS_DEFAULT_OTP')
default_otp = os.getenv('DEFAULT_OTP')

def get_otp_for_email(email, session):
    # Get the login user email verified
    user_details = get_user_details(session, {'email': email.lower()})
    
    if user_details:
        if not user_details.is_active:
            session.close()
            raise HTTPException(status_code=403, detail="User is not active")
        
        # Generate OTP
        otp = generate_otp() if not is_default_otp.lower() == 'true' else default_otp
        user_updatedat = user_details.updated_at
        
        # Update OTP and OTP time in the user table
        otp_time = round(time.time())
        update_user_details(session, {'email': email.lower()}, {'otp': otp, 'otp_time': otp_time, 'updated_at': user_updatedat})
        subject = "Your Verification Code - Do Not Share"
        content_to_be_sent = f"""
<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OTP Verification</title>
        <style>
            /* Include the CSS from the artifact here */
            body, table, td, p, a, li, blockquote {{
                -webkit-text-size-adjust: 100%;
                -ms-text-size-adjust: 100%;
            }}
            
            body {{
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                line-height: 1.6;
            }}
            
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 40px 30px;
                text-align: center;
                color: white;
            }}
            
            .header h1 {{
                margin: 0;
                font-size: 28px;
                font-weight: 600;
            }}
            
            .header p {{
                margin: 10px 0 0 0;
                font-size: 16px;
                opacity: 0.9;
            }}
            
            .content {{
                padding: 40px 30px;
                text-align: center;
            }}
            
            .content h2 {{
                color: #333333;
                font-size: 24px;
                margin: 0 0 20px 0;
                font-weight: 600;
            }}
            
            .content p {{
                color: #666666;
                font-size: 16px;
                margin: 0 0 30px 0;
                line-height: 1.6;
            }}
            
            .otp-container {{
                background-color: #f8f9ff;
                border: 2px dashed #667eea;
                border-radius: 12px;
                padding: 30px;
                margin: 30px 0;
                display: inline-block;
            }}
            
            .otp-code {{
                font-size: 36px;
                font-weight: bold;
                color: #667eea;
                letter-spacing: 8px;
                font-family: 'Courier New', monospace;
                margin: 0;
            }}
            
            .otp-label {{
                font-size: 14px;
                color: #888888;
                margin: 10px 0 0 0;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .warning {{
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 6px;
                padding: 20px;
                margin: 30px 0;
                color: #856404;
            }}
            
            .warning-icon {{
                font-size: 20px;
                margin-right: 8px;
            }}
            
            .expiry-time {{
                color: #e74c3c;
                font-weight: 600;
            }}
            
            .footer {{
                background-color: #f8f9fa;
                padding: 30px;
                text-align: center;
                border-top: 1px solid #e9ecef;
            }}
            
            .footer p {{
                color: #6c757d;
                font-size: 14px;
                margin: 0 0 10px 0;
            }}
            
            .company-name {{
                color: #667eea;
                font-weight: 600;
            }}
            
            @media only screen and (max-width: 600px) {{
                .email-container {{
                    width: 100% !important;
                    border-radius: 0 !important;
                }}
                
                .header, .content, .footer {{
                    padding: 30px 20px !important;
                }}
                
                .otp-code {{
                    font-size: 28px !important;
                    letter-spacing: 4px !important;
                }}
                
                .header h1 {{
                    font-size: 24px !important;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1>🔐 Verification Required</h1>
                <p>Secure access to your account</p>
            </div>
            
            <div class="content">
                <h2>Your One-Time Password</h2>
                <p>We received a request to verify your identity. Please use the verification code below to complete your authentication:</p>
                
                <div class="otp-container">
                    <div class="otp-code">{otp}</div>
                    <p class="otp-label">Verification Code</p>
                </div>
                
                <div class="warning">
                    <span class="warning-icon">⚠️</span>
                    <strong>Important:</strong> This code will expire in <span class="expiry-time">5 minutes</span>. 
                    Do not share this code with anyone for security reasons.
                </div>
                
                <p>If you didn't request this verification code, please ignore this email or contact our support team immediately.</p>
            </div>
            
            <div class="footer">
                <p>© 2025 Your Company. All rights reserved.</p>
                <p style="font-size: 12px; margin-top: 20px;">
                    If you have any questions, please contact us at subscription@codework.ai
                </p>
            </div>
        </div>
    </body>
    </html>
"""

        send_email(email, subject, content_to_be_sent)
        # Prepare response
        AuthResponseDetails.status = 200
        AuthResponseDetails.message = f'OTP has been sent to your Email'
        session.commit()
        session.close()
        return AuthResponseDetails
    else:
        session.close()
        raise HTTPException(status_code=404, detail="User not found")