from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Load the CSV data once when the app starts to avoid reloading it every time
data = pd.read_csv('data/data.csv')

# Helper function to generate pie chart
def generate_pie_chart(transport, hotel, food):
    labels = ['Transport', 'Hotel', 'Food']
    sizes = [transport, hotel, food]
    colors = ['#ff9999', '#66b3ff', '#99ff99']
    
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Save the pie chart to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    
    # Return the image as a base64-encoded string
    return base64.b64encode(img.getvalue()).decode('utf8')

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Capture form data
        selected_country = request.form.get('country')
        selected_city = request.form.get('city')
        transport_mode = request.form.get('transport_mode')
        stay_duration = request.form.get('stay_duration')
        currency_mode = request.form.get('currency_mode')

        # Initialize values
        total_cost = 0
        total_cost_dollars = 0
        cost_breakdown = {}
        
        # Ensure all required fields are filled before calculation
        if selected_city and transport_mode and stay_duration:
            stay_duration = int(stay_duration)

            # Get data for the selected city
            city_data = data[(data['Country'] == selected_country) & (data['City'] == selected_city)]
            if not city_data.empty:
                city_data = city_data.iloc[0]

                # Safely retrieve transport cost
                transport_cost = city_data.get(f'{transport_mode}_INR', 0)
                hotel_cost = city_data['Hotel_Cost_per_night_INR'] * stay_duration
                food_cost = city_data['Food_Cost_per_day_INR'] * stay_duration

                total_cost = transport_cost + hotel_cost + food_cost

                # Create the cost breakdown dictionary
                cost_breakdown = {
                    'Transport': transport_cost,
                    'Hotel': hotel_cost,
                    'Food': food_cost
                }

                # Handle USD conversion
                if currency_mode == 'usd':
                    conversion_rate = 75  # Assuming a fixed conversion rate
                    total_cost_dollars = total_cost / conversion_rate
                    cost_breakdown = {k: v / conversion_rate for k, v in cost_breakdown.items()}

                # Redirect to the results page
                return redirect(url_for('results', 
                                        total_cost=total_cost, 
                                        total_cost_dollars=total_cost_dollars, 
                                        transport_cost=cost_breakdown['Transport'], 
                                        hotel_cost=cost_breakdown['Hotel'], 
                                        food_cost=cost_breakdown['Food'], 
                                        pie_chart_img=generate_pie_chart(cost_breakdown['Transport'], cost_breakdown['Hotel'], cost_breakdown['Food']),
                                        selected_country=selected_country,
                                        selected_city=selected_city))

    # Get countries for the dropdown
    countries = data['Country'].unique()
    return render_template('index.html', countries=countries)

@app.route('/results')
def results():
    total_cost = request.args.get('total_cost', type=float)
    total_cost_dollars = request.args.get('total_cost_dollars', type=float)
    transport_cost = request.args.get('transport_cost', type=float)
    hotel_cost = request.args.get('hotel_cost', type=float)
    food_cost = request.args.get('food_cost', type=float)
    pie_chart_img = request.args.get('pie_chart_img')
    
    # Get the selected country and city to populate the form for the next calculation
    selected_country = request.args.get('selected_country')
    selected_city = request.args.get('selected_city')
    
    # Fetch available cities for the selected country
    available_cities = data[data['Country'] == selected_country]['City'].unique() if selected_country else []

    return render_template('result.html', total_cost=total_cost, 
                           total_cost_dollars=total_cost_dollars, 
                           transport_cost=transport_cost, 
                           hotel_cost=hotel_cost, 
                           food_cost=food_cost,
                           pie_chart_img=pie_chart_img,
                           selected_country=selected_country,
                           selected_city=selected_city,
                           available_cities=available_cities)

@app.route('/get_cities/<country>')
def get_cities(country):
    cities = data[data['Country'] == country]['City'].unique()
    return jsonify(cities.tolist())

if __name__ == '__main__':
    app.run(debug=True)
