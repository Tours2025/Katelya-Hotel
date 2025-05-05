from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get bot token from environment variables or use default
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7965204613:AAHSui33BbEb_xZELg32STQ-spidi609YSQ')

# Configure recipients - individual chat and channel
PERSONAL_CHAT_ID = os.environ.get('PERSONAL_CHAT_ID', '709944787')  # Your personal chat ID
CHANNEL_CHAT_ID = os.environ.get('CHANNEL_CHAT_ID', '-1002501641816')  # Your channel chat ID

# Create a list of all recipients
CHAT_IDS = [PERSONAL_CHAT_ID, CHANNEL_CHAT_ID]

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    """Simple route to check if the server is running."""
    return 'Telegram Bot Server is running!'

@app.route('/send-reservation', methods=['POST'])
def send_reservation():
    """Endpoint to receive reservation data and forward it to Telegram."""
    try:
        # Get form data from the request
        data = request.json
        logger.info(f"Received reservation data: {data}")
        
        # Extract reservation details, with flexible field names to handle both
        # tour guide requests and taxi service requests
        name = data.get('name', '')
        phone = data.get('phone', '')
        
        # Handle different date/time formats
        tour_date = data.get('tourDate', data.get('date', ''))
        tour_time = data.get('tourTime', data.get('time', ''))
        
        # Handle different service types
        service_type = data.get('serviceType', 'Hotel Service Request')
        
        # Other fields with fallbacks
        duration = data.get('duration', '')
        participants = data.get('participants', '')
        guide_language = data.get('guideLanguage', '')
        room = data.get('room', 'Not staying at hotel')
        special_interests = data.get('specialInterests', '')
        notes = data.get('notes', 'No notes provided')
        
        # Format the message based on service type
        if "Taxi" in service_type:
            # Format for taxi service
            message = f"""
🚕 *NEW TAXI SERVICE REQUEST* 🚕

🏨 *Service Type:* {service_type}
👤 *Name:* {name}
📞 *Phone:* {phone}
📅 *Date:* {tour_date}
⏱️ *Time:* {tour_time}
🛏️ *Room Number:* {room}
📝 *Notes:* {notes}
            """
        else:
            # Format for tour guide service (default)
            message = f"""
🏨 *NEW TOUR RESERVATION* 🏨

👤 *Name:* {name}
📞 *Phone:* {phone}
📅 *Tour Date:* {tour_date}
⏱️ *Duration:* {duration}
👥 *Participants:* {participants}
🗣️ *Guide Language:* {guide_language}
🛏️ *Room Number:* {room}
🎯 *Special Interests:* {special_interests}
📝 *Notes:* {notes}
            """
        
        # Send message to all configured Telegram recipients
        success_count = 0
        error_messages = []
        
        for chat_id in CHAT_IDS:
            if not chat_id.strip():
                continue
                
            telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                'chat_id': chat_id.strip(),
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            logger.info(f"Sending message to Telegram chat ID {chat_id}")
            response = requests.post(telegram_url, json=payload)
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('ok'):
                success_count += 1
                logger.info(f"Message sent successfully to chat ID {chat_id}")
            else:
                error_message = f"Failed to send message to chat ID {chat_id}: {response_data}"
                error_messages.append(error_message)
                logger.error(error_message)
        
        # Return the appropriate response based on the results
        if success_count > 0:
            return jsonify({
                'success': True,
                'message': f'Reservation sent to {success_count} recipient(s) successfully',
                'errors': error_messages if error_messages else None
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send message to any recipients',
                'errors': error_messages
            }), 500
            
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to process reservation',
            'error': str(e)
        }), 500

@app.route('/test-bot', methods=['GET'])
def test_bot():
    """Test endpoint to check if the bot is working with all recipients."""
    try:
        success_count = 0
        results = []
        
        for chat_id in CHAT_IDS:
            if not chat_id.strip():
                continue
                
            # Send a test message to each chat ID
            telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                'chat_id': chat_id.strip(),
                'text': f"🧪 *Bot Test Message*\n\nThis is a test message to verify that your bot is working correctly. Sending to chat ID: {chat_id}",
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(telegram_url, json=payload)
            response_data = response.json()
            
            result = {
                'chat_id': chat_id,
                'success': response.status_code == 200 and response_data.get('ok'),
                'response': response_data
            }
            
            if result['success']:
                success_count += 1
                
            results.append(result)
        
        return jsonify({
            'success': success_count > 0,
            'message': f'Test message sent to {success_count} out of {len(CHAT_IDS)} recipient(s)',
            'results': results
        })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to send test message',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 8080))
    
    # Display configured chat IDs on startup
    logger.info(f"Configured chat IDs: {CHAT_IDS}")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port)