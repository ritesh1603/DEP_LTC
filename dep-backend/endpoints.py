from flask import request, session, Blueprint
from functions import createNewLTCApplication, listLiveApplications, listLiveTAApplications, listDoneLTCApplications
from nonApplicantEndpoints import router as nonApplicantRouter
from models import LTCInfo, TAInfo, db, Notification, User, Receipt
import uuid
import mimetypes
import json
import os
from typing import List
import csv
import io
from flask import jsonify
from datetime import datetime,timezone
router = Blueprint("endpoints", __name__)
router.register_blueprint(nonApplicantRouter)

# need checking

def uploadReceipts(ltc):
    return "what"

def deletehelper(data):

    user_to_delete = User.query.filter_by(emailId=data).first()

    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
        return  'User deleted successfully', 200
    else:
        return 'User not found', 404



@router.route('/deleteuser', methods=['POST'])
def delete_user():
    data = json.loads(request.form['json'])
    print(data)

    email = data.get('Email')

    user_to_delete = User.query.filter_by(emailId=email).first()

    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
        return  'User deleted successfully', 200
    else:
        return 'User not found', 404

#geting the user detail from the email id
@router.route('/getUserByEmail', methods=["POST"])
def get_user_by_email():
    try:
        data = request.get_json()
        email = data.get("email")
        
        print(email)
        if not email:
            return jsonify({"error": "Email not provided"}), 400

        user = User.query.filter_by(emailId=email).first()

        if user:
            return jsonify(user.json()), 200
        else:
            return jsonify({"error": "User not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500




@router.route('/createNewLTCApplications', methods=['POST'])
def createNewLTCApplicationHandle():
    ltcInfo = json.loads(request.form['json'])
    userInfo = session.get('userInfo')
    print(userInfo)
    ltc = createNewLTCApplication(userInfo, ltcInfo)
    return "Done", 200


@router.route('/addusercsv', methods=['POST'])
def add_users():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file', 400
    
    if file:
        # Parse the CSV file

        csv_data = io.TextIOWrapper(file, encoding='utf-8')
        
        reader = csv.reader(csv_data)
        for row in reader:
            user = {
                'firstName': row[0],
                'lastName': row[1],
                'emailId': row[2],
                'hometown': row[3],
                'designation': row[4],
                'payLevel': row[5],
                'roleId': row[6],
                'dateOfJoining': row[7],
                'department': row[8],
                'last_notification_check' :datetime.now()
            }
            new_user = User(user)

            db.session.add(new_user)
            db.session.commit()
        
        return 'Users added successfully', 200


@router.route('/newuser', methods=['POST'])
def newuser():
    data = json.loads(request.form['json'])
    print(data)
    # Extract user information from the request data
    first_name = data.get('First Name')
    last_name = data.get('Last Name')
    email = data.get('Email')
    hometown = data.get('Hometown')
    designation = data.get('Designation')
    pay_level = data.get('Pay Level')
    role_id = data.get('roleId')
    date_of_joining = data.get('Date Of Joining')
    department = data.get('Department')

    # # ... add other fields as needed

    new_user = User(
        {'firstName' : first_name,
        'lastName' : last_name,
        'emailId' :email,
        'hometown' :hometown,
        'designation': designation,
        'payLevel': pay_level,
        'roleId': role_id,
        'dateOfJoining': date_of_joining,
        'department': department,
        'last_notification_check' :datetime.now()
        }
    )

    # # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return "User created successfully", 200

@router.route('/updatePayLevel', methods=['GET', 'POST'])
def update_paylevel():
    data = request.get_json()  
    email = data.get('email')
    new_pay_level = data.get('newPayLevel')

    user = User.query.filter_by(emailId=email).first()

    if user:
        # Update the user's pay level
        user.payLevel = new_pay_level
        db.session.commit()
        return 'Pay level updated successfully', 200
    else:
        return 'User not found', 404



@router.route('/deleteusercsv', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        
        file = request.files['file']
        
        if file.filename == '':
            return "No selected file"
        
        if file:
            # Process the CSV file
            names_to_delete = []
            for line in file:
                names_to_delete.append(line.decode().strip())  # Assuming one name per line
            
            for names in names_to_delete:
                deletehelper(names)
            # Delete users from the database
            # for names in names_to_delete:
            #     Users.query.filter
            
            
            return "Users deleted successfully"
    
    return 'Upload CSV file' , 404

# endpoint to print all the users

@router.route('/displayUsers', methods=['GET'])
def display_users():
    users = User.query.all()
    user_list = [user.json() for user in users]
    return jsonify(user_list)



# @router.route('/createNewTAApplication', methods=['POST'])
# def createNewTAAApplicationHandle():
#     json_data = json.loads(request.form['json'])
#     journeyDetails = json_data.get('journeyDetails')
#     userInfo = session.get('userInfo')
#     ltcId = json_data.get('ltcId')
#     LTCInfo.query.filter(LTCInfo.id == ltcId).first().stageCurrent = 101
#     taInfo = TAInfo(userId=userInfo.id,
#                     ltcId=ltcId,
#                     journeyDetails=journeyDetails)

#     for file in request.files.getlist('file'):
#         fileName = uuid.uuid4().hex + mimetypes.guess_extension(file.mimetype)
#         base_path = os.path.join(os.path.dirname(__file__), 'receipts')
#         filePath = f"{base_path}/{fileName}"
#         taInfo.receipts.append(Receipt(filePath))
#         print(file.save(filePath))

#     db.session.add(taInfo)
#     db.session.commit()
#     print(taInfo.json())
#     # print(taInfo.json())
#     return "Done", 200

# # working fine
@router.route('/createNewTAApplication', methods=['POST'])
def createNewTAAApplicationHandle():
    json_data = json.loads(request.form['json'])
    journeyDetails = json_data.get('journeyDetails')
    userInfo = session.get('userInfo')
    ltcId = json_data.get('ltcId')
    LTCInfo.query.filter(LTCInfo.id == ltcId).first().stageCurrent = 101
    
    # Extract certificate data from the request data
    certificateData = {
        'blockYear': json_data.get('blockYear'),
        'OtherThanHometown': json_data.get('OtherThanHometown'),
        'GovtOffice': json_data.get('GovtOffice')
    }

    # Create TAInfo instance with certificate data
    taInfo = TAInfo(
        userId=userInfo.id,
        ltcId=ltcId,
        journeyDetails=journeyDetails,
        certificate=certificateData,
    )

    # Handle file uploads
    for file in request.files.getlist('file'):
        fileName = uuid.uuid4().hex + mimetypes.guess_extension(file.mimetype)
        base_path = os.path.join(os.path.dirname(__file__), 'receipts')
        filePath = f"{base_path}/{fileName}"
        taInfo.receipts.append(Receipt(filePath))
        print(file.save(filePath))

    # Commit TAInfo instance to the database
    db.session.add(taInfo)
    db.session.commit()
    
    # Print TAInfo JSON representation for debugging
    print(taInfo.json())
    
    # Return response
    return "Done", 200



@router.route('/listLiveLTCApplications', methods=['POST', 'GET'])
def listLiveLTCApplicationHandle():
    userInfo = session.get('userInfo')
    ltcInfos = [ltc.json() for ltc in listLiveApplications(userInfo)]
    return ltcInfos

# working fine


@router.route('/listDoneLTCApplications', methods=['POST'])
def listDoneLTCApplicationsHandle():
    userInfo = session.get('userInfo')
    taInfos = [ta.json() for ta in listDoneLTCApplications(userInfo)]
    return taInfos
    pass


@router.route('/getLTCInfo', methods=['POST'])
def getLTCInfo():
    ltcId = request.json.get('ltcId')
    ltcInfo = LTCInfo.query.filter_by(id=ltcId).first()
    if (ltcInfo):
        print(ltcInfo.json())
        return ltcInfo.json(), 200
    # return ltcInfo.json(), 200
    return {}, 400

@router.route('/getOldLTCInfo', methods=['POST'])
def getOldLTCInfo():
    ltcId = request.json.get('ltcId')
    ltcInfo: LTCInfo = LTCInfo.query.filter(LTCInfo.id==ltcId).first()
    if (ltcInfo):
        ltcs = LTCInfo.query.filter(LTCInfo.userId == ltcInfo.userId).all()
        if(len(ltcs) > 1): return ltcs[-2].json(), 200
    # return ltcInfo.json(), 200
    return {}, 400

@router.route('/listLiveTAApplications', methods=['POST'])
def listLiveTAApplicationsHandle():
    userInfo = session.get('userInfo')
    taInfos = [ta.json() for ta in listLiveTAApplications(userInfo)]
    return taInfos
    pass


@router.route('/getTAInfo', methods=['POST'])
def getTAInfo():
    taId = request.json.get('taId')
    print(taId)
    taInfo = TAInfo.query.filter_by(id=taId).first()
    print(taId)
    # print(taInfo.json())
    if (taInfo):
        # print(taInfo.json())
        return taInfo.json(), 200
    return {}, 401


@router.route('/getNotifications', methods=["POST"])
def getNotifications():
    user = User.query.filter(User.id == session.get('userInfo').id).first()
    if (user):
        # user.last_notification_check = datetime.now()
        # db.session.commit()
        notifications = user.notifications
        return list(reversed([n.json() for n in notifications]))
    return [], 401

@router.route('/updateNotificationsTime', methods=["POST"])
def updateNotificationsTime():
    user = User.query.filter(User.id == session.get('userInfo').id).first()
    if (user):
        user.last_notification_check = datetime.now()
        db.session.commit()
        return [],201
    return [], 401

@router.route('/getNotificationsCount', methods=["POST"])
def getNotificationsCount():
    user = User.query.filter(User.id == session.get('userInfo').id).first()
    if user:
        notifications = user.notifications
        new_notifications = [n for n in notifications if n.time > user.last_notification_check]
        count = len(new_notifications)
        print(count)
        return jsonify({"count": count}), 200
    else:
        return jsonify({"error": "User not found"}), 404


@router.route('/listLTCOfficeOrders', methods=['POST'])
def listLTCOfficeOrder():
    handlerInfo = session.get('userInfo')
    if (handlerInfo.id == 0):
        list(reversed([j.json() for j in LTCInfo.query.filter(LTCInfo.userId == handlerInfo.id, LTCInfo.stageCurrent >= 100).all()]))
    return list(reversed([j.json() for j in LTCInfo.query.filter(LTCInfo.stageCurrent >= 100).all()]))


@router.route('/listTAOfficeOrders', methods=['POST'])
def listTAOfficeOrder():
    handlerInfo = session.get('userInfo')
    if(handlerInfo.id ==0): 
        list(reversed([j.json() for j in TAInfo.query.filter(TAInfo.userId == handlerInfo.id, TAInfo.stageCurrent >= 100).all()]))
    return list(reversed([j.json() for j in TAInfo.query.filter(TAInfo.stageCurrent >= 100).all()]))


@router.route('/getComments', methods=['POST'])
def getComments():
    ltcFormId = request.json.get('id')
    # print('ltcId', ltcId)
    # ltcInfo = LTCInfo.query.filter(LTCInfo.id==ltcId).first()
    ltcInfo: LTCInfo = LTCInfo.query.filter_by(id=ltcFormId).first()

    return [comment.json() for comment in ltcInfo.comments]
    # return {}


@router.route('/getTAComments', methods=['POST'])
def getTAComments():
    taFormId = request.json.get('id')
    # print('ltcId', ltcId)
    # ltcInfo = LTCInfo.query.filter(LTCInfo.id==ltcId).first()
    taInfo: TAInfo = TAInfo.query.filter_by(id=taFormId).first()

    return [comment.json() for comment in taInfo.comments]
    # return {}


@router.route('/getReceipt', methods=['POST'])
def getReceipt():
    fileId = request.json.get('fileId')
    if(fileId):
        receipt = Receipt.query.filter(Receipt.id == fileId).first()
        if(receipt):
            print(receipt.filePath)
    
    return "200"


