from flask import Flask, render_template, request, redirect, flash,jsonify ,session , url_for
import psycopg2
from psycopg2 import OperationalError
from datetime import datetime
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import json
import os


with open("config.json", "r") as c:
    params = json.load(c)["params"]

donation = Flask(__name__)
donation.secret_key = 'donate'

# def create_connection():
#     try:
#         connection = psycopg2.connect(
#             user="postgres",
#             password="postgres",
#             host="localhost",
#             port="5432",
#             database="food_donation"
#         )
#         return connection
#     except OperationalError as e:
#         print(f"❌ The error '{e}' occurred")
#         return None

def create_connection():
    try:
        connection = psycopg2.connect(
            user="root",
            password=params['postgres_pass'],
            host=params['postgres_host'],
            port="5432",
            database="food_donation"
        )
        return connection
    except OperationalError as e:
        print(f"❌ The error '{e}' occurred")
        return None

# def create_tables():
#     """Create tables if they don't exist"""
#     connection = create_connection()
#     if connection:
#         try:
#             cursor = connection.cursor()
            
#             # Create information table
#             cursor.execute("""
#                 CREATE TABLE IF NOT EXISTS information (
#                     id SERIAL PRIMARY KEY,
#                     name VARCHAR(50) NOT NULL,
#                     phone VARCHAR(10) NOT NULL,
#                     email VARCHAR(50) NOT NULL,
#                     password VARCHAR(100) NOT NULL
#                 )
#             """)
            
#             # Create food_donation_form table
#             cursor.execute("""
#                 CREATE TABLE IF NOT EXISTS food_donation_form (
#                     donation_id SERIAL PRIMARY KEY,
#                     name VARCHAR(50) NOT NULL,
#                     phone VARCHAR(10) NOT NULL,
#                     address VARCHAR(100) NOT NULL,
#                     date DATE NOT NULL,
#                     quantity INTEGER NOT NULL,
#                     food_name VARCHAR(100) NOT NULL
#                      user_id INTEGER
#                 )
#             """)
            
#             connection.commit()
#             print("✅ Tables created successfully")
            
#         except Exception as e:
#             print(f"❌ Error creating tables: {e}")
#         finally:
#             cursor.close()
#             connection.close()



llm = ChatGroq(
    model_name="gemma2-9b-it",
    temperature=1,
    api_key = params['GROQ_API_KEY']

)

# Assuming you used HuggingFaceEmbeddings to create the vectorstore
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"
embeddings = HuggingFaceEmbeddings(
    model="all-MiniLM-L6-v2", # Ensure you have this in your .env or config
)

try:
    # Load your existing FAISS vectorstore
    loaded_vectorstore = FAISS.load_local(
        "ngo_vectorstore", # Ensure this path is correct relative to where app.py runs
        embeddings,
        allow_dangerous_deserialization=True # Necessary if you saved with allow_dangerous_deserialization=True
    )
    # Create the RAG chain
    rag_prompt_template = """
    You are a helpful assistant for Hope Harvest Foundation, a food donation NGO.
    Use the following context to answer the question about the NGO.

    Context: {context}

    Question: {question}
    Important Notes:
    'Please provide a helpful and accurate answer based on the context provided.
    Clean and reformat answer. Remove all extra spaces and asterisk (*) symbols. Ensure the output is in a proper structured format, using consistent spacing, punctuation, and formatting as needed.'
    If the question is not related to the NGO or cannot be answered from the context,
    politely redirect the user to ask about NGO-related topics.

    Answer:
    """
    RAG_PROMPT = PromptTemplate(
        template=rag_prompt_template,
        input_variables=["context", "question"]
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=loaded_vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        ),
        chain_type_kwargs={"prompt": RAG_PROMPT},
        return_source_documents=False # We only need the answer for the chatbot
    )
    print("RAG chain initialized successfully.")

except Exception as e:
    print(f"Error loading vectorstore or initializing RAG chain: {e}")
    qa_chain = None # Handle case where RAG fails to load









# Create tables on startup
# create_tables()

@donation.route('/login', methods=['GET', "POST"])
def login():
    return render_template('userlogin.html')

@donation.route('/logout', methods=['GET'])
def logout():
    for i in list(session.keys()):
        session.pop(i)
    return render_template('userlogin.html')

@donation.route('/', methods=['GET', "POST"])
def home():
    if 'username' in session:
        # User is logged in, retrieve username from session
        username = session['username']
        return render_template('home.html', username=username)
    else:
        return render_template('home.html', username=None)

@donation.route('/login_access', methods=['GET', "POST"])
def login_access():
    email = request.form['email']
    password = request.form['password']
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT name ,id FROM information WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()
            if user:
                session['username'] = user[0]  # Store username in session for later use
                session['user_id'] = user[1]
                return render_template('home.html', username=user[0])
            else:
                flash('email or password is wrong')
                return redirect('/login')
                
        except Exception as e:
            return redirect('/login')
        finally:
            cursor.close()
            connection.close()
    else:
        flash('Database connection failed')
        return redirect('/login')

@donation.route('/add_info', methods=['GET', "POST"])
def add_info():
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Check if user already exists by email
            cursor.execute("SELECT id FROM information WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            # Check if user already exists by name
            cursor.execute("SELECT id FROM information WHERE name = %s", (name,))
            user1 = cursor.fetchone()
            
            if password == confirm_password and not user and not user1:
                cursor.execute(
                    "INSERT INTO information (name, phone, email, password) VALUES (%s, %s, %s, %s)",
                    (name, phone, email, password)
                )
                cursor.execute("SELECT name ,id FROM information WHERE email = %s AND password = %s", (email, password))
                user = cursor.fetchone()
                connection.commit()
                print("User added successfully")
                session['username'] = user[0]  # Store username in session for later use
                session['user_id'] = user[1]  # Store username in session for later use

                return render_template('home.html', username=session['username'])
            elif user or user1:
                flash("user already exist!")
                return redirect('/signup')
            elif password != confirm_password:
                flash("confirm_password doesn't match with password!")
                return redirect('/signup')
                
        except Exception as e:
            flash('Database error occurred')
            return redirect('/signup')
        finally:
            cursor.close()
            connection.close()
    else:
        flash('Database connection failed')
        return redirect('/signup')

@donation.route('/signup')
def signup():
    return render_template('usersignup.html')

@donation.route('/donate_food')
def donate_food():
    return render_template('useraftersignup.html')

@donation.route('/add_donation', methods=['GET', "POST"])
def add_donation():
    try:
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        date = request.form['date']
        quantity = request.form['quantity']
        food_name = request.form['foodName']
        user_id = session.get('user_id')  # Get user ID from session if needed
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()

                    # Convert date string to proper format if needed
                try:
                    date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                except ValueError:
                        # Try different date format if the first one fails
                    date_obj = datetime.strptime(date, '%m/%d/%Y').date()
                    
                cursor.execute(
                        "INSERT INTO food_donation_form (name, phone, address, date, quantity, food_name, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (name, phone, address, date_obj, quantity, food_name, user_id)
                    )
                connection.commit()
                flash('Thank you for donating!')
                return render_template('home.html', username=session.get('username'))
                
                    
            except Exception as e:
                flash('Something went wrong please try again!')
                return redirect('/donate_food')
            finally:
                cursor.close()
                connection.close()
        else:
            flash('Database connection failed')
            return redirect('/donate_food')
            
    except Exception as e:
        flash('Something went wrong please try again!')
        return redirect('/donate_food')






# --- Helper Functions for Chatbot Logic ---

# 1. Router Agent
def classify_intent(user_message: str, llm) -> str:
    """Classifies the user's message intent."""
    classification_prompt = f"""
    Classify the following message based on the user's intent.
    Respond with only ONE word: 'NGO_INFO', 'DONATION', or 'OTHER'.

    'NGO_INFO': The user is asking a question about the organization, its activities, contact details, location, or general information.
    'DONATION': The user expresses intent to donate food or is providing details related to a food donation (like name, address, food type, quantity).
    'OTHER': The message is unrelated to asking about the NGO or making a food donation.

    Message: "{user_message}"

    Classification:
    """
    try:
        response = llm.invoke(classification_prompt)
        # Clean up the response to get just the single word
        intent = response.content.strip().upper()
        if intent in ['NGO_INFO', 'DONATION', 'OTHER']:
            return intent
        else:
            print(f"Warning: Classifier returned unexpected intent: {intent}. Defaulting to OTHER.")
            return 'OTHER' # Fallback for unexpected outputs
    except Exception as e:
        print(f"Error during intent classification: {e}")
        return 'OTHER' # Fallback on error

# 2. RAG Function (Integrated via qa_chain)
def get_ngo_info_response(user_question: str, qa_chain) -> str:
    """Gets response from the RAG chain."""
    if not qa_chain:
        return "Sorry, the information retrieval system is currently unavailable."
    try:
        result = qa_chain.invoke({"query": user_question}) # Use invoke
        # The result structure might vary slightly depending on the chain setup
        # For RetrievalQA without return_source_documents=True, it's often result['result']
        return result.get('result', 'Sorry, I could not find information related to your question.')
    except Exception as e:
        print(f"Error during RAG query: {e}")
        return "Sorry, I encountered an error trying to retrieve information."


# 3. Donation Data Extraction and Flow Management
REQUIRED_DONATION_FIELDS = ['name', 'phone', 'address', 'date', 'quantity', 'food_name']

def handle_donation_input(user_message: str, current_donation_info: dict, llm) -> tuple[str, dict]:
    """
    Handles input during the donation collection flow.
    Extracts info, updates state, and generates response.
    Returns (bot_response, updated_state).
    """
    # Ensure donation_info has all required fields, even if None
    donation_info = {field: current_donation_info.get(field) for field in REQUIRED_DONATION_FIELDS}
    initial_state = all(value is None for value in donation_info.values()) # Check if we're just starting

    todays_date = datetime.now().strftime('%Y-%m-%d') # Get today's date for reference
    # Use LLM to extract information from the message
    extraction_prompt = f"""
    The user wants to donate food and is providing information.
    Extract the following details from the user's message: Name, Phone, Address, Date, Quantity, Food Name.
    Only extract information that is explicitly present in the message and corresponds to the field.
    List the extracted information in a simple "Field: Value" format.
    If multiple pieces of information are found for a single field, list them all (e.g., "Name: John Doe, Name: Jane Smith").
    If no relevant information is found in the message, just respond with "No info found."
    This is Todays date: {todays_date}.
    I want Date in format of '%Y-%m-%d' so if user gives date in different format then convert it to '%Y-%m-%d' format.
    Inportant notes:
    - If the user provides a date, ensure it is in the format '%Y-%m-%d'.
    - If user provide phone number, ensure it is in the format of 10 digits. and only one phone number be extract.
    Example:
    User: My name is Alice and I want to donate 10 kgs of rice tomorrow at 3pm. My number is 1234567890.
    Extraction:
    Name: Alice
    Quantity: 10 kgs
    Food Name: rice
    Phone: 1234567890
    Date: Give date as per todays date and user provided date in format of '%Y-%m-%d'.

    User: I live at 123 Main St.
    Extraction:
    Address: 123 Main St

    User: Ok, thanks.
    Extraction:
    No info found.

    Current known information:
    {', '.join([f'{field}: {value}' for field, value in donation_info.items() if value is not None]) if not initial_state else 'None yet.'}

    User message: "{user_message}"

    Extraction:
    """

    extracted_text = ""
    try:
        extraction_response = llm.invoke(extraction_prompt)
        extracted_text = extraction_response.content.strip()
    except Exception as e:
        print(f"Error during information extraction: {e}")
        # Continue without extracted info if LLM call fails
        extracted_text = "No info found."


    # Parse the extracted text and update donation_info
    if extracted_text != "No info found.":
        lines = extracted_text.split('\n')
        for line in lines:
            if ': ' in line:
                field, value = line.split(': ', 1)
                field = field.strip().lower().replace(' ', '_') # Normalize field name
                if field in REQUIRED_DONATION_FIELDS:
                    # Simple append logic - could be improved for specific fields (e.g., consolidating addresses)
                    if donation_info[field] is None:
                        donation_info[field] = value.strip()
                    else:
                        # Append if user gives more info for the same field
                        donation_info[field] += f", {value.strip()}"


    # Check which fields are still missing
    missing_fields = [field for field in REQUIRED_DONATION_FIELDS if donation_info.get(field) is None or donation_info.get(field).strip() == '']

    bot_response = ""
    new_state_mode = 'donation_collection' # Default to staying in collection mode

    if not missing_fields:
        # All information collected
        print("Donation Info Collected:", donation_info) # Simulate saving to DB/processing

        # --- SIMULATE DATABASE INSERTION HERE ---
        # In a real application, you would save donation_info to your database
        # For now, we just print it and provide a confirmation message.
        print("--- Simulating Saving Donation to Database ---")
        print(f"Name: {donation_info['name']}")
        print(f"Phone: {donation_info['phone']}")
        print(f"Address: {donation_info['address']}")
        print(f"Date: {donation_info['date']}")
        print(f"Quantity: {donation_info['quantity']}")
        print(f"Food Name: {donation_info['food_name']}")
        print("---------------------------------------------")
        # --- END SIMULATION ---
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                
                if donation_info:
                    # Convert date string to proper format if needed
                    
                    
                    cursor.execute(
                        "INSERT INTO food_donation_form (name, phone, address, date, quantity, food_name, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (donation_info['name'], donation_info['phone'], donation_info['address'], donation_info['date'], donation_info['quantity'], donation_info['food_name'],session.get('user_id'))
                    )
                    connection.commit()
                    flash('Thank you for donating!')
                    
                else:
                    flash('No donation information provided.')
                                     
                    
            except Exception as e:
                flash('Something went wrong please try again!')
                
            finally:
                cursor.close()
                connection.close()
        

        bot_response = "Thank you! I have collected all the necessary information for your food donation. We will process this and be in touch if needed."
        new_state_mode = 'initial' # Reset mode
        donation_info = {} # Clear collected info

    elif initial_state and extracted_text == "No info found.":
        # User initiated donation but provided no info in the first message
        bot_response = "Okay, I can help you with donating food. What is your name, phone number, address, the date you'd like to donate, the quantity, and the type of food?"

    elif extracted_text != "No info found." and missing_fields:
         # Info extracted but some fields are still missing
        missing_fields_str = ", ".join([field.replace('_', ' ') for field in missing_fields])
        bot_response = f"Thank you! I got some information. Could you please also provide your {missing_fields_str}?"

    elif extracted_text == "No info found." and missing_fields:
        # No info extracted and fields are still missing - reprompt for missing ones
        missing_fields_str = ", ".join([field.replace('_', ' ') for field in missing_fields])
        bot_response = f"I didn't get that. Could you please tell me the following missing information for your donation: {missing_fields_str}?"

    else:
         # Catch-all - should ideally not happen if logic is sound
         bot_response = "Okay, what else can I help you with regarding your donation?"


    # Return the generated response and the updated donation state
    return bot_response, {'mode': new_state_mode, 'donation_info': donation_info}




@donation.route('/send_message', methods=['POST'])
def send_message():
    """Receives a message via POST, routes it, and sends a response."""
    data = request.get_json()
    user_message = data.get('message', '').strip() # Get message and strip whitespace

    if not user_message:
        return jsonify({'response': "Please type a message."})

    # Get or initialize chatbot state from session
    # State structure: {'mode': 'initial' | 'ngo_info' | 'donation_collection', 'donation_info': {}}
    state = session.get('chatbot_state', {'mode': 'initial', 'donation_info': {}})
    # print(f"--- Current state: {state} ---") # Debugging

    bot_response = ""
    next_state = state.copy() # Start with the current state
    
    # --- Core Logic: Route the message ---

    # If we are currently in the donation collection mode, assume the message is for donation
    if state.get('mode') == 'donation_collection':
        print("Routing to: Donation Collection (due to state)")
        bot_response, updated_donation_state = handle_donation_input(user_message, state.get('donation_info', {}), llm)
        next_state['donation_info'] = updated_donation_state['donation_info']
        next_state['mode'] = updated_donation_state['mode'] # handle_donation_input might change mode back to 'initial'

    else:
        # Otherwise, use the intent classifier (Router Agent)
        intent = classify_intent(user_message, llm)
        print(f"Routing to: {intent} (based on classification)")

        if intent == 'NGO_INFO':
            if qa_chain:
                bot_response = get_ngo_info_response(user_message, qa_chain)
            else:
                 bot_response = "Sorry, I cannot provide information about the NGO at this moment."
            next_state['mode'] = 'initial' # Reset mode after answering
            next_state['donation_info'] = {} # Clear any partial donation info if switching

        elif intent == 'DONATION':
            # Start the donation collection flow
            next_state['mode'] = 'donation_collection'
            bot_response, updated_donation_state = handle_donation_input(user_message, {}, llm) # Start with empty info
            next_state['donation_info'] = updated_donation_state['donation_info']
            next_state['mode'] = updated_donation_state['mode'] # Check if it completed immediately

        else: # OTHER or unclear
            bot_response = "I can help you with questions about Hope Harvest Foundation or assist you with making a food donation. What would you like to do?"
            next_state['mode'] = 'initial' # Reset mode
            next_state['donation_info'] = {} # Clear any partial donation info if switching


    # Save the updated state to the session
    session['chatbot_state'] = next_state
    # print(f"--- New state: {session['chatbot_state']} ---") # Debugging

    # Return the bot's response
    return jsonify({'response': bot_response})


@donation.route('/alldonation')
def alldonation():
    """
    Displays all donation records for the logged-in user.
    Requires the user to be logged in.
    """
    # Check if the user is logged in
    username = session.get('username') # Assuming username is also stored for display

    if not username:
        flash("Please log in to view your donations.")
        return redirect(url_for('login')) # Redirect to your login route
    user_donations_data = []
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(
                        "SELECT name, phone, address, date, quantity, food_name From food_donation_form WHERE user_id = %s ORDER BY date DESC",
                        (int(session.get("user_id")),)
                    )
        user_donations_data = cursor.fetchall()
    except Exception as e:
        # Handle database errors gracefully
        print(f"Database error fetching donations for user '{username}': {e}")
        flash(f"An error occurred while fetching your donations: {e}")
        user_donations_data = [] # Return an empty list if there's an error

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    # Render the template, passing the donations data and username
    return render_template('alldonation.html',
                           donations=user_donations_data,
                           username=username)



if __name__ == "__main__":
    donation.run()
    
    
    
