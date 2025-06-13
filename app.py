import streamlit as st
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

# Twilio credentials
TWILIO_ACCOUNT_SID = "AC0061533eda6b5dd58b201bd943f11927"
TWILIO_AUTH_TOKEN = "c99e4435c963ba743355c775665bec8b"
TWILIO_PHONE_NUMBER = "+18313026534"

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# In-memory storage for reminders
reminders = []

# Scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Function to send WhatsApp message
def send_whatsapp_message(to_number, message):
    try:
        client.messages.create(
            body=message,
            from_='whatsapp:+14155238886',  # Twilio sandbox WhatsApp number
            to=f'whatsapp:+91{to_number}'   # Add country code and prefix with 'whatsapp:'
        )
        print(f"WhatsApp message sent to {to_number}: {message}")
    except Exception as e:
        print(f"Failed to send WhatsApp message to {to_number}: {e}")

# Function to send SMS message
def send_sms(to_number, message):
    try:
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=f'+91{to_number}'  # Add country code for SMS
        )
        print(f"SMS message sent to {to_number}: {message}")
    except Exception as e:
        print(f"Failed to send SMS message to {to_number}: {e}")

# Schedule a job 10 minutes before the reminder time
def schedule_reminder(medicine_name, to_number, reminder_time):
    send_time = reminder_time - timedelta(minutes=10)
    if send_time < datetime.now():
        send_time = datetime.now() + timedelta(seconds=5)  # fallback to immediate if past
    def job():
        send_whatsapp_message(to_number, f"Reminder: In 10 minutes, it's time to take your medicine '{medicine_name}'")
        send_sms(to_number, f"Reminder: In 10 minutes, it's time to take your medicine '{medicine_name}'")
    scheduler.add_job(job, 'date', run_date=send_time)

# Streamlit UI
def main():
    st.title("💊 Medicine Reminders, Right in Your Chat!")

    with st.form("reminder_form"):
        medicine_name = st.text_input("Medicine Name")
        phone_number = st.text_input("Phone Number   (Do not put country code since it is only functionable in India)")
        reminder_date = st.date_input("Reminder Date")
        reminder_time = st.time_input("Reminder Time  (Give time atleast 10 mins before the reminder time)")
        submitted = st.form_submit_button("Set Reminder")

        if submitted:
            if not medicine_name or not phone_number:
                st.error("Please enter both medicine name and phone number.")
            else:
                reminder_datetime = datetime.combine(reminder_date, reminder_time)
                now = datetime.now()
                if reminder_datetime <= now + timedelta(minutes=10):
                    st.error("Reminder time must be at least 10 minutes from now.")
                else:
                    reminders.append({
                        "medicine_name": medicine_name,
                        "phone_number": phone_number,
                        "reminder_time": reminder_datetime
                    })

                    schedule_reminder(medicine_name, phone_number, reminder_datetime)
                    st.success(f"Reminder set for '{medicine_name}' at {reminder_datetime.strftime('%Y-%m-%d %H:%M:%S')} (you'll be notified 10 minutes before)")

    st.subheader("Scheduled Reminders")
    for r in reminders:
        st.write(f"{r['medicine_name']} – {r['phone_number']} at {r['reminder_time'].strftime('%Y-%m-%d %H:%M:%S')} (Reminder 10 min before)")

if __name__ == "__main__":
    main()
