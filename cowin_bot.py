import constrants as keys
from telegram.ext import *
from telegram import *
import requests
from datetime import datetime

# Adding headers
header={
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}

print("Bot started...")


# creating start Command Handler

def start_command(update,context):
	update.message.reply_text('Welcome to Covid Vaccine centre tracker.\n Type "Vaccine Center near me"---To find the Vaccine centre near you')
# creating help command handler
def help_command(update,context):
	update.message.reply_text('Type "Vaccine Center near me"---To find the Vaccine centre near you')
# creating state command handler
def state_handler(name):
	URL = 'https://cdn-api.co-vin.in/api/v2/admin/location/states'
	state_name = str(name).title()
	response = requests.get(URL,headers=header)
	response_json = response.json()
	data = response_json["states"]
	flag = 0
	
	for each in data:
		if each['state_name'] == state_name:
			id_state = each['state_id']
			flag = 1
			break
	if flag == 1:
		return id_state
	else:
		return
		
# creating distict command handler	

def district_handler(name,id):
	query = 'https://cdn-api.co-vin.in/api/v2/admin/location/districts/{}'.format(id) 
	district_name = str(name).title()
	response = requests.get(query,headers=header)
	response_json = response.json()
	data = response_json["districts"]
	flag=0
	for each in data:
		if each['district_name'] == district_name:
			id = each['district_id']
			flag = 1
			break
	if flag == 1:
		return id
	else:
		return

def pincode_handler(pincode):
	
	print(pincode)
	now = datetime.now()
	date = now.strftime("%d-%m-%Y")
	URL='https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={}&date={}'.format(pincode,date)
	response = requests.get(URL,headers=header)
	return response


def message_handler(update,context):
	global c
	global state_id
	text = str(update.message.text).lower()
	#print(text)
	if text == 'vaccine center near me' and c==0:
		update.message.reply_text('Search by Pincode or Search by District')
		#update.message.reply_text('Enter the State Name')
		c=1
	elif text == 'search by pincode' and c==1:
		update.message.reply_text('Enter the Pincode')
		c=2

	elif c==2:
		response = pincode_handler(text)
		response_json = response.json()
		if not response_json["centers"]:
			update.message.reply_text('No vaccine centers avaliable under this pincode.Try again!!')
					
		else:
			for center in response_json["centers"]:
				for session in center["sessions"]:

					update.message.reply_text('center_id: {} \nCenter Name: {}\nAddress: {}\nPinecode: {}\nfee_type: {}\nDate: {} \navailable_capacity: {}\nVaccine: {}\nAvailable_capacity_dose1: {}\nAvailable_capacity_dose2: {}\nMinimum age limit: {}\nslot:{}'.format(center["center_id"]
																														,center["name"]
																														,center["address"]
																														,center['pincode']
																														,center['fee_type']
																														,session['date']
																														,session["available_capacity"]
																														,session['vaccine']
																														,session['available_capacity_dose1']
																														,session['available_capacity_dose2']
																														,session["min_age_limit"]
																														,session["slots"]))

			c=0
			


	elif text == 'search by district' and c==1:
		update.message.reply_text('Enter the State name')
		c=3

	elif c==3: 
		state_id = state_handler(text)
		if state_id:
			update.message.reply_text('Enter the District Name')
			c = 4
		else:
			update.message.reply_text('Wrong State name!!Try again')
			
		
	elif c==4:
		district_id = district_handler(text,state_id)
		if district_id:

			now = datetime.now()
			today_date = now.strftime("%d-%m-%Y")
			search = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?district_id={}&date={}'.format(district_id,today_date)
			response = requests.get(search,headers=header)
			response_json = response.json()
			data = response_json["sessions"]
			flag=0
			for each in data:
				if each["available_capacity"] > 0:
					flag=1
					update.message.reply_text('center_id: {} \nCenter Name: {}\nAddress: {}\nPinecode: {}\nfee_type: {}\nfee: {} \navailable_capacity: {}\nVaccine: {}\nAvailable_capacity_dose1: {}\nAvailable_capacity_dose2: {}\nMinimum age limit: {}\nslot:{}'.format(each["center_id"]
																													,each["name"]
																													,each["address"]
																													,each['pincode']
																													,each['fee_type']
																													,each['fee']
																													,each["available_capacity"]
																													,each['vaccine']
																													,each['available_capacity_dose1']
																													,each['available_capacity_dose2']
																													,each["min_age_limit"]
																													,each["slots"]))

			c=0
			if flag == 0:
				update.message.reply_text("No vaccine avaliable at the centers near you right now!\nTry after sometime")
		else:
			update.message.reply_text('Wrong district name!!Try again')

	else:
		update.message.reply_text("Sorry I don't understand you\n Type '/help' for any help")

		
		

def error(update,context):
	print(f"update{update} caused error{context.error}")

if __name__=="__main__":
	global c
	c =0 
	updater =Updater(keys.API_key,use_context=True)
	dp = updater.dispatcher
	dp.add_handler(CommandHandler("start",start_command))
	dp.add_handler(CommandHandler("help",help_command))
	dp.add_handler(MessageHandler(Filters.text, message_handler))
	dp.add_error_handler(error)
	updater.start_polling()
	updater.idle()
	



