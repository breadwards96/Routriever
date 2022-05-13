# @Bread 2022-1-1 bedwards@hickmanseggs.com

import datetime
import smtplib
import ssl
import Crypto

import pandas as pd
from suds.client import Client

# Get Config Settings
try:
    config = open("config")
    config_list = config.readlines()
except FileNotFoundError:
    print("Config File Not Found")

web_service = config_list[0].strip()
key_file = config_list[1].strip()
username = config_list[2].strip()
appname = config_list[3].strip()
branches = config_list[4].split(',')
example_route = config_list[5].strip()
route_output = config_list[6].strip()
info_output = config_list[7].strip()
sending_mail = config_list[8].strip()
receiving_mail = config_list[9].strip()
config.close()


def createClient():
    # Create client and connect to web service
    client = Client(web_service)  # Redact

    return client


# ///////// authentication func
def get_auth_token(client):
    print("Generating Authentication Token")

    enc_pass = b'gAAAAABiUFkg8i5fPx8yc5ih0QJXEWv9Sb_mhPWD0MHbcQgB1ykjkTzDzfxvjbKMJp0n96JiaNVpuQfX7UOADxC8q0Q7YEszYw=='

    try:
        enc_file = open(key_file)
        key = enc_file.read()
        enc_file.close()
        dec_pass = Crypto.decrypt(enc_pass, key)
    except FileNotFoundError:
        try:
            enc_file = open("key.txt")
            key = enc_file.read()
            enc_file.close()
            dec_pass = Crypto.decrypt(enc_pass, key)
        except FileNotFoundError:
            print("Key file not found")
            dec_pass = ""

    # Create Authentication Token and build Authentication type to send
    auth_response_env = client.service.GetAuthenticationToken(username, dec_pass.decode(), appname)

    token = auth_response_env.authenticationField.authenticationTokenField

    auth = client.factory.create('ns0:Authentication')

    auth.authenticationTokenField = token

    return auth


# /////// setup Func
def setup(client):
    # Filling required fields in request envelope
    # OrderType = client.factory.create("ns0:OrderType")

    route_detail_request_envelope = client.factory.create('ns0:RouteDetailRequestEnvelope')

    tomorrow = datetime.datetime(datetime.date.today().year, datetime.date.today().month,
                                 datetime.date.today().day) + datetime.timedelta(days=1)
    thirty_day = tomorrow + datetime.timedelta(days=30)

    route_detail_request_envelope.fromDateField = tomorrow
    route_detail_request_envelope.toDateField = thirty_day

    print("Grabbing routes from date: " + str(tomorrow) + " to date: " + str(thirty_day) + "\n")

    return_options = route_detail_request_envelope.routeDetailReturnOptionsField.filtersField

    return_options.populatePreassignmentsField = True
    return_options.populateRouteFormsField = True
    return_options.populateStopField = True
    return_options.populateUserFieldField = True
    return_options.populateOrderField = True
    return_options.populateOrderFormsField = True
    return_options.populatePlannedDataField = True

    return_options.populateActualsDataField = False
    return_options.populateGPSPointsField = False
    return_options.populateQuantityFieldField = False
    return_options.populateLineItemField = False
    return_options.populateLineItemFormsField = False
    return_options.populateTrucksField = False
    return_options.populateViolationsField = False

    return_options.routeTypeField = "AllRoute"

    search_options = route_detail_request_envelope.routeDetailSearchByOptionsField

    search_options.value = "DispatchDate"

    client.set_options()

    return route_detail_request_envelope


# ///////// mainLoop Func
def mainLoop(client, authentication, branch_list, route_detail_request_envelope):
    # Looping through all branches collecting routes
    # Construct DataFrame to store dicts before export
    df = pd.DataFrame()
    one = 0
    for b in range(len(branch_list)):

        print("Branch: " + str(branch_list[b]))

        # Calling Web Service
        route_detail_request_envelope.branchIDField = branch_list[b]
        route_details = client.service.GetRouteDetailByModifiedDate(authentication, route_detail_request_envelope)
        try:
            detail_list = route_details.routeDetailListField.RouteDetailResponseEnvelopeRouteDetail
            print(str(len(detail_list)) + " route(s) on this branch\n")
        except AttributeError:
            print("No routes for this branch\n")
            continue

        while one < 1:
            try:
                routes = open(example_route, "w")
                routes.write(str(route_details))
                routes.close()
                one += 1
            except FileNotFoundError:
                break

        # Getting details from each route
        route = 0
        while route < len(detail_list):
            plan = detail_list[route].planField

            stop_num = 0
            # Get each stop on the route
            while stop_num < len(plan.stopField.StopPlanDetailType):

                new_dict = {"branchIDField": branch_list[b], "dispatchIDField": "", "routeIDField": "",
                            "dispatchDateField": "", "startTimeField": "", "endTimeField": "",
                            "lastDateModifiedField": "", "routeExportStatusField": "", "totalLegsField": "",
                            "totalDriveHrsField": "", "totalWorkHrsField": "", "driverEmployeeIdField": "",
                            "driverIDField": "", "driverNameField": "", "isTerminalField": "", "legField": "",
                            "sequenceField": "", "estimateStartTimeField": "", "estimateEndTimeField": "",
                            "fixedTimeField": "", "breakTimeField": "", "layoverTimeField": "", "latitudeField": "",
                            "longitudeField": "", "orderKeyIDField": "", "stopIDField": "", "waitTimeField": "",
                            "accountIDField": "", "eqCodeField": "", "orderIDField": "", "address1Field": "",
                            "cityField": "", "stateField": "", "zipCodeField": "", "totalDistanceField": "",
                            "distanceField": ""}

                # Getting plan items
                plan_items = ["dispatchIDField", "routeIDField", "dispatchDateField", "startTimeField", "endTimeField",
                              "lastDateModifiedField", "routeExportStatusField", "totalLegsField", "totalDriveHrsField",
                              "totalWorkHrsField", "totalDistanceField"]
                i = 0
                while i < len(plan_items):
                    plan_item = plan_items[i]
                    new_dict[plan_item] = plan.__getitem__(plan_items[i])
                    i += 1

                # Getting preassignment items
                preass_items = ["driverEmployeeIdField", "driverIDField", "driverNameField"]
                preass = detail_list[route].preassignmentField
                t = 0
                while t < len(preass_items):
                    try:
                        new_dict[preass_items[t]] = preass.__getitem__(preass_items[t])
                        t += 1
                    except AttributeError:
                        break

                # Getting stop items
                stop_items = ["isTerminalField", "legField", "sequenceField", "estimateStartTimeField", "distanceField",
                              "estimateEndTimeField", "fixedTimeField", "breakTimeField", "layoverTimeField",
                              "stopIDField"]
                stop = plan.stopField.StopPlanDetailType[stop_num]
                si = 0
                while si < len(stop_items):
                    stop_item = str(stop_items[si])
                    new_dict[stop_item] = stop.__getitem__(stop_items[si])
                    si += 1

                # Getting order details for each order
                order_items = ["accountIDField", "eqCodeField", "orderIDField", "orderKeyIDField"]
                try:
                    order = plan.stopField.StopPlanDetailType[stop_num].orderField.OrderDetailPlanDetailType[0]
                except AttributeError:
                    print("Malformed stop on route: " + str(new_dict.get('dispatchIDField')) +
                          "\nDate: " + str(new_dict.get('dispatchDateField')) + "\nSTOP OMITTED\n")
                    email_alert(new_dict)
                    stop_num += 1
                    continue
                j = 0

                while j < len(order_items):
                    order_item = str(order_items[j])
                    new_dict[order_item] = order.__getitem__(order_items[j])
                    j += 1

                # Getting address details for each order
                address_items = ["address1Field", "cityField", "stateField", "zipCodeField"]
                address = plan.stopField.StopPlanDetailType[stop_num].shipToAddressField
                x = 0
                while x < len(address_items):
                    address_item = str(address_items[x])
                    new_dict[address_item] = address.__getitem__(address_items[x])
                    x += 1

                coord_items = ["latitudeField", "longitudeField"]
                coords = plan.stopField.StopPlanDetailType[stop_num].shipToAddressField.coordinatesField

                c = 0
                while c < len(coord_items):
                    coord_item = str(coord_items[c])
                    new_dict[coord_item] = coords.__getitem__(coord_items[c])
                    c += 1

                stop_num += 1

                # Fixing datetime conflicts
                for item in new_dict:
                    if isinstance(new_dict[item], type(datetime.datetime(1, 1, 1, 1, 1, 1))):
                        new_date = datetime.datetime(new_dict[item].year, new_dict[item].month,
                                                     new_dict[item].day, new_dict[item].hour, new_dict[item].minute,
                                                     new_dict[item].second)
                        new_dict[item] = new_date
                # Constructing a new DataFrame and appending all orders together
                df2 = pd.DataFrame(new_dict, index=[0])
                df = pd.concat([df, df2], ignore_index=True)
            route += 1
    return df


# ///////// export Func
def export(df):
    # Export to CSV
    print("Transferring data to csv \n")
    try:
        df.to_csv(route_output, index=False, index_label=False)
        print("Finished")
        status = 'Success'
    except PermissionError:
        print("Export Failed, close 'routes.csv' and run again")
        status = 'Failed'
    except OSError:
        print(r"Smartconnect routes file not found")
        print("exporting to run location")
        df.to_csv("routes.csv", index=False, index_label=False)
        print("Finished\n")
        status = 'Success'

    return status


# ///////// log Func
def log(status):
    try:
        current_time = datetime.datetime.now()
        inf = open(info_output, 'w+')  # Redact
        inf.write('Last Run: ' + str(current_time) + '\n' + 'Run Status: ' + status)
        inf.close()
    except FileNotFoundError:
        print('Smartconnect info.txt file not found')


def email_alert(partial_dict):
    # port = 0  # SSL port
    enc_pass = b'gAAAAABiUFxHDS5Jmk6z8roYCg_vUci-E3vBtCuDgbq7TGsYINroQNAAu1XN7eomj07zjTZoz2ayLLwMFSH5PAZbcHs-0rFKcA=='

    try:
        enc_file = open(key_file)
        key = enc_file.read()
        enc_file.close()
        password = Crypto.decrypt(enc_pass, key)
    except FileNotFoundError:
        try:
            enc_file = open("key.txt")
            key = enc_file.read()
            enc_file.close()
            password = Crypto.decrypt(enc_pass, key)
        except FileNotFoundError:
            print("Key file not found")
            password = ""

    smtp_server = "smtp.gmail.com"
    sender_email = sending_mail
    receiver_email = receiving_mail
    message = "STOP OMITTED FROM FILE: " + str(partial_dict.get('dispatchIDField')) + \
              " Date: " + str(partial_dict.get('dispatchDateField'))

    # Create SSL Context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server, context=context) as server:
        server.login(sending_mail, password.decode())
        server.sendmail(sender_email, receiver_email, message)


clientInst = createClient()
auth_token = get_auth_token(clientInst)
RDRE = setup(clientInst)
frame = mainLoop(clientInst, auth_token, branches, RDRE)
run_status = export(frame)
log(run_status)
