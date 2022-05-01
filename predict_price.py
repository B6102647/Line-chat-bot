import pymongo
import warnings
import numpy as np
import pandas as pd
import math

from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense,LSTM


scaler = MinMaxScaler(feature_range=(0,1))

warnings.filterwarnings('ignore')

# connect to the mongoclient
client = pymongo.MongoClient('mongodb+srv://manuschanok:01032542@linebot.orvrw.mongodb.net/LineBot?retryWrites=true&w=majority')

# get the database
database = client['LineBot']

def find_stock(stock_name):
    if stock_name == 'AAPL' or stock_name == 'aapl':
        col = database["aapl"]
    elif stock_name == 'TSLA' or stock_name == 'tsla':
        col = database["tsla"]
    elif stock_name == 'EGCO.BK' or stock_name == 'egco.bk':
        col = database["egco"]
    elif stock_name == 'PTT.BK' or stock_name == 'ptt.bk':
        col = database["ptt"]
    elif stock_name == 'SMD.BK' or stock_name == 'smd.bk':
        col = database["smd"]
    elif stock_name == 'PFE' or stock_name == 'PFE':
        col = database["pfe"]
    else:
        return 
    cursor = col.find({})
    dataset = pd.DataFrame.from_dict(cursor)
    return dataset


def find_model(df):
    data = df.filter(['Price'])
    dataset = data.values
    training_data_len = math.ceil(len(dataset)*0.8)

    scaled_data = scaler.fit_transform(dataset)

    train_data = scaled_data[0:training_data_len,:]

    x_train = []
    y_train = []

    for i in range(60, len(train_data)):
        x_train.append(train_data[i-60:i,0])
        y_train.append(train_data[i,0])

    x_train,y_train = np.array(x_train),np.array(y_train)

    x_train = np.reshape(x_train, (x_train.shape[0],x_train.shape[1],1))
    
    #Build the LSTM model
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(x_train.shape[1],1)))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dense(25))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mean_squared_error')

    model.fit(x_train,y_train,batch_size=40,epochs=3)

    return model

def find_last_60_mins(df): 
    #get the last 60 minutes price values and convert to an array
    last_60_mins = df[-60:].values
    # Scale the data to be values between 0 and 1
    last_60_mins_scaled = scaler.transform(last_60_mins)
    # Create an empty list
    X_test = []
    # Append the past 60 minutes
    X_test.append(last_60_mins_scaled)
    # Convert the X_test data set to a numpy array
    X_test = np.array(X_test)
    # Reshape the data
    X_test = np.reshape(X_test, (X_test.shape[0],X_test.shape[1], 1))
    # print(new_df)
    return X_test

def predict_price(name,status):

    df = find_stock(name)
    model = find_model(df)

    df = df.filter(['Price'])
    X_test = find_last_60_mins(df)
    count = 0
    if status == 'open':
        next_5_min = []
        
        for i in range (0,5):
            # Get the predicted 
            pred_price = model.predict(X_test)
            pred_price = scaler.inverse_transform(pred_price)
            
            add_to_df = pd.DataFrame({"Price" : pred_price.tolist()[0]})

            df = df.append(add_to_df,ignore_index=True)

            next_5_min.append(pred_price)
            X_test = find_last_60_mins(df)
            # count+=1
            # print("predict price =",pred_price[0][0])
    else:
        pred_price = model.predict(X_test)
        pred_price = scaler.inverse_transform(pred_price)
        # print("predict price =",pred_price[0][0])
        # count+=1
    # print(next_5_min)
    # print("next 5 minute price predict is ",pred_price)
    # print("count =",count)
    return pred_price[0][0]

# predict_price('AAPL','open')
# predict_price('AAPL','close')
# print(predict_price('AAPL','close'))




