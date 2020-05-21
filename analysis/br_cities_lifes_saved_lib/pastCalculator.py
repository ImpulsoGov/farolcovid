import os
old_path = os.getcwd()
os.chdir("..")
os.chdir("src") #Workaround to import two important modules
import model.seir as seir
import loader
os.chdir(old_path) #goes back to the old path
import yaml
import numpy as np
import pandas as pd
import scipy.integrate
import scipy.optimize
import dateutil.parser
import datetime
import plotly.express as px

def read_local_data(country, config, endpoint): #adapted from loader.read_data()

    api_url = config[country]["api"]["local"]
    url = api_url + endpoint["cases"]
    #print(url)

    df = pd.read_csv(url)

    if "last_updated" in df.columns:
        # fix types
        df["last_updated"] = df["last_updated"].replace("0", np.nan)
        # df["is_last"] = df["is_last"].astype(bool)
        df[[c for c in df.columns if "last_updated" in c]] = df[
            [c for c in df.columns if "last_updated" in c]
        ].apply(pd.to_datetime)

    return df

#THIS CODE MAKES A FIT TO THE HISTORICAL NUMBER OF DEATHS IN A CITY VARYING ALL OF THE PARAMETERS OF THE SIER SIMULATION
#Except for "mild_duration", "severe_duration" and "critical_duration" and of course the city's parameters (population,etc)
#and notification rate (which we get from the simulacovid data for each city)
#Warning, this model is only good for big cities with a month or more of a constant report of deaths
#Recomended amount of days to look into the past -> 30
#config = yaml.load(open('configs/config.yaml', 'r'), Loader = yaml.FullLoader) #Configuration file we are going to use
config = loader.config#importing from loader
#STILL WE USE ONLY LOCAL DATA
spid = 3550308 #ID of São Paulo city - SP just as an example for testing
#loader.read_data
cities = read_local_data('br', config, endpoint=config['br']['api']['endpoints']['analysis']) #We are using the full data so it might take a bit to load
#Calculates how many recovered patients we have
#user_input -> {'population_params':{'R':number,'I':number , 'D' : number}}
#selected_day -> Data from the cities (above) dataframe but one row for one city in one day
#notification_rate -> Self explanatory
def calculate_recovered(user_input, selected_day, notification_rate): #Adapted from the one found in simulation.py

        confirmed_adjusted = int(selected_day['confirmed_cases']/notification_rate) #changed this part to go straight to our selected day part

        if confirmed_adjusted == 0: # dont have any cases yet
                user_input['population_params']['R'] = 0
                return user_input

        user_input['population_params']['R'] = confirmed_adjusted - user_input['population_params']['I'] - user_input['population_params']['D']

        if user_input['population_params']['R'] < 0:
                user_input['population_params']['R'] = confirmed_adjusted - user_input['population_params']['D']

        return user_input

#Gets from the city id the city's parameters from n days before (available arg)
def getSimInput(cityid,nDaysBefore=30):    
    #initialize user
    dates = cities.loc[cities['city_id'] == cityid]["last_available_date"] #gets the dates we have data on abuot the city
    last_date = dateutil.parser.parse(dates.iloc[-1])
    new_date = last_date - datetime.timedelta(days = nDaysBefore) #date n days before
    new_date_str = str(new_date.date())
    dados_do_dia = cities.loc[cities['city_id'] == cityid].loc[cities["last_available_date"] == new_date_str].iloc[-1] #gets the row corresponding to that city in that day

    user_input = dict()

    notification_rate = dados_do_dia['notification_rate']
    # POP USER INPUTS (This time, city parameters), but used to be user inputs in simulacovid
    user_input['population_params'] = {'N': int(dados_do_dia['estimated_population_2019'])}
    user_input['population_params']['D'] = int(dados_do_dia['deaths'])

    # get infected cases
    infectious_period = config['br']['seir_parameters']['severe_duration'] + config['br']['seir_parameters']['critical_duration']

    if dados_do_dia['confirmed_cases'] == 0:
        raise Exception("Not enough case history to make a calculation")
    else:
        user_input['population_params']['I'] = int(dados_do_dia['infectious_period_cases'] / notification_rate)

    # calculate recovered cases and adds it to user_input
    user_input = calculate_recovered(user_input, dados_do_dia, notification_rate)

    return user_input["population_params"] #returns the city's parameters


#Return a list of the amoun of deaths in the last n days of this city (progressively)
def getDeaths(city_id,n_days=30):
    dates = cities.loc[cities['city_id'] == city_id]["last_available_date"]
    last_date = dateutil.parser.parse(dates.iloc[-1])
    new_ref_date = last_date - datetime.timedelta(days = n_days)
    new_date_str = str(new_ref_date.date())
    days_data = cities.loc[cities['city_id'] == city_id]
    days_data = days_data.loc[days_data ["last_updated"] >= new_ref_date]
    deaths = days_data["deaths"].values #same date procedure and the extracts the values of the last n days of deaths
    return deaths

def getDefaultDiseaseParameters():
        return config["br"]["seir_parameters"]
#order of the arguments in the function, very important
order = ["fatality_ratio","doubling_rate","incubation_period","i1_percentage","i2_percentage","i3_percentage","infected_health_care_proportion","R"]


#Extracts only the missing parameters from the default config so we can use it as a initial guess for our fit model
def getHistoricalArgs(default_model_parameters):
    dp = default_model_parameters
    hist_args = [dp[i] for i in order[:-1]]
    hist_args.append(2) # R=2 is our historical initial guess

#Generates our amount of deaths function (the simulation that tells, given a set of parameters, how many days occured in our system on day d)
#this is the function we are going to use for our fit
#This function below is generating that function from the city's initial conditions
def genDeathsFunc(city_id,n_days):
    def deathsFunc(day,fatality_ratio,doubling_rate,incubation_period,i1_percentage,i2_percentage,i3_percentage,infected_health_care_proportion,R):
        model_parameters_in = locals()
        initial = False
        default_population_params_in = getSimInput(city_id,n_days)
        default_model_parameters_in = getDefaultDiseaseParameters()
        model_parameters_in["mild_duration"] = default_model_parameters_in["mild_duration"]
        model_parameters_in["severe_duration"] = default_model_parameters_in["severe_duration"]
        model_parameters_in["critical_duration"] = default_model_parameters_in["critical_duration"]
        del model_parameters_in["R"]
        population_params, model_params = seir.prepare_states(default_population_params_in, model_parameters_in), seir.prepare_params(default_population_params_in, model_parameters_in, R)
        params = {'y0': list(population_params.values()),
                't': np.linspace(0, n_days, n_days+1), 
                'args': (model_params, initial)}
        total_result = pd.DataFrame(scipy.integrate.odeint(seir.SEIR, **params), columns=['S', 'E' ,'I1', 'I2', 'I3', 'R', 'D'])
        real_result = total_result["D"][day]
        return real_result
    return deathsFunc

#MAIN FUNCTION: Will, given the id of a city and how many days ago you want to consider the start, calculate what sets of arguments yields the 
#best fitting curve for the SEIR model
def findCurve(city_id,n_days=30):
    default_population_params_in = getSimInput(city_id,n_days)
    historical_args = getHistoricalArgs(getDefaultDiseaseParameters())
    deathsHistorical = getDeaths(city_id,n_days)
    #([position i is min of arg i],[position i is max of arg i])
    plannedBounds = ([0.00001,1,1,0.00001,0.00001,0.00001,0.00001,0.0001], [1., 3, 20,1.,1.,1.,1.,10]) #Very important and subject to future tweaks
    #function to calculate our deaths as a function of each argument
    deathsFunc =  genDeathsFunc(city_id,n_days)
    results = scipy.optimize.curve_fit(deathsFunc, np.linspace(0, n_days, n_days+1),deathsHistorical,p0=historical_args, bounds=plannedBounds)
    float_results_args = [float(i) for i in results[0]]
    results_dict = dict()
    for a,i in enumerate(order):
        results_dict[i] = float_results_args[a]
    return results_dict
#Given a set of multipliers for R, will generate the lists of historical deaths + deaths in each day for each scenario
#Example, if multipliers = [1,2,3,4] it will result in a matrix [historical deaths series ,death series for R=R0, death series for R=2*R0, death series for R=3*R0 ...]
def compareNumerically(city_id,n_days = 30,multipliers=[1,2,0.5]):
    results = findCurve(city_id,n_days) #gets the fit
    deathsHistorical = getDeaths(city_id,n_days)
    deathsFunc = genDeathsFunc(city_id,n_days) #gets a deathsFunc to calculate different scenarios
    a1,a2,a3,a4,a5,a6,a7,a8 = [i for i in results.values()] #unpacks it
    deathsMatrix = []
    deathsMatrix.append([float(i) for i in deathsHistorical]) #add the historical deaths first
    for mult in multipliers:
        deathsCalc = []
        for t in range(n_days):
            deaths = deathsFunc(t,a1,a2,a3,a4,a5,a6,a7,mult*a8)
            deathsCalc.append(deaths)
        deathsMatrix.append(deathsCalc)
    return deathsMatrix

def compareScenariosWithPlots(city_id,num_days=30,min=0.5,max=2):
    days = [i for i in range(num_days)]
    city_name = cities.loc[cities['city_id'] == city_id]["city"].iloc[0]
    scenarios_for_city = compareNumerically(city_id,n_days = num_days,multipliers=[1,max,min])
    #labels
    days_column_name = "Days beginning %d days in the past"%(num_days)
    deaths_columns_name = "Deaths in %s"%(city_name)
    min_label = r" $%0.4f \cdot R_0$" % min
    max_label = r" $%0.4f \cdot R_0$" % max
    #data frame creation
    data_dict = {days_column_name:days,deaths_columns_name:scenarios_for_city[0][:-1],"type":["Historical" for i in range(len(days))]}
    data_dict2 = {days_column_name:days,deaths_columns_name:scenarios_for_city[1],"type":["Fitted" for i in range(len(days))]}
    data_dict3 = {days_column_name:days,deaths_columns_name:scenarios_for_city[2],"type":[max_label for i in range(len(days))]}
    data_dict4 = {days_column_name:days,deaths_columns_name:scenarios_for_city[3],"type":[min_label for i in range(len(days))]}
    df1 = pd.DataFrame(data_dict)
    df1 = df1.append(pd.DataFrame(data_dict2))
    df1 = df1.append(pd.DataFrame(data_dict3))
    df1 = df1.append(pd.DataFrame(data_dict4))
    #creating the figure
    fig = px.line(df1, x=days_column_name, y=deaths_columns_name, color="type", hover_name=deaths_columns_name,
            line_shape="spline", render_mode="svg",title='Evolution of Deaths in %s in different possible scenarios for the past'%city_name)
    max_deaths_dif = scenarios_for_city[2][-1]-scenarios_for_city[0][:-1][-1]
    min_deaths_dif = scenarios_for_city[0][:-1][-1] - scenarios_for_city[3][-1]
    return fig,min_deaths_dif,max_deaths_dif
