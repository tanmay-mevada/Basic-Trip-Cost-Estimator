import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

class CityCostModel:
    def __init__(self):
        self.data = pd.read_csv('data/data.csv')
        self.model = None
        self.train_model()

    def train_model(self):
        # Preprocessing - selecting relevant features for training
        X = self.data[['Distance', 'Hotel_Cost_per_night_INR', 'Food_Cost_per_day_INR']]
        y = self.data[['Airfare_INR', 'Train_Fare_INR', 'Bus_Fare_INR']].sum(axis=1)  # Summing transport costs

        # Splitting data for training and testing
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Training linear regression model
        self.model = LinearRegression()
        self.model.fit(X_train, y_train)

    # Method to return unique countries from the dataset
    def get_countries(self):
        return self.data['Country'].unique()

    def get_cities(self, country):
        return self.data[self.data['Country'] == country][['City', 'Distance']].to_dict('records')

    def calculate_cost(self, country, city, transport_mode, stay_duration, currency_mode):
        if not stay_duration or not stay_duration.isdigit():
            print("Invalid stay duration")
            return None, None  # Returning early in case of invalid stay_duration
    
        stay_duration = int(stay_duration)
        
        city_data = self.data[(self.data['Country'] == country) & (self.data['City'] == city)]
        
        if city_data.empty:
            print("City data is empty")
            return None, None  # Return None if no matching city data
    
        city_data = city_data.iloc[0]
    
        transport_column_map = {
            'Airfare': 'Airfare_INR',
            'Train': 'Train_Fare_INR',
            'Bus': 'Bus_Fare_INR'
        }
    
        transport_cost = city_data.get(transport_column_map.get(transport_mode), 0)
        hotel_cost = city_data['Hotel_Cost_per_night_INR'] * stay_duration
        food_cost = city_data['Food_Cost_per_day_INR'] * stay_duration
    
        total_cost = transport_cost + hotel_cost + food_cost
        cost_variation_percent = 0.1
        min_cost = total_cost * (1 - cost_variation_percent)
        max_cost = total_cost * (1 + cost_variation_percent)
    
        if currency_mode == 'usd':
            conversion_rate = 75
            min_cost_usd = min_cost / conversion_rate
            max_cost_usd = max_cost / conversion_rate
            cost_breakdown = {
                'Transport': transport_cost / conversion_rate,
                'Hotel': hotel_cost / conversion_rate,
                'Food': food_cost / conversion_rate,
                'Min_USD': min_cost_usd,
                'Max_USD': max_cost_usd
            }
        else:
            cost_breakdown = {
                'Transport': transport_cost,
                'Hotel': hotel_cost,
                'Food': food_cost,
                'Min_INR': min_cost,
                'Max_INR': max_cost
            }
    
        print(f"Cost Breakdown: {cost_breakdown}")
        return (min_cost, max_cost), cost_breakdown
    
    