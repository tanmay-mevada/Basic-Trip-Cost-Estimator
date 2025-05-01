import matplotlib.pyplot as plt
import io
import base64

def generate_pie_chart(transport, hotel, food):
    labels = ['Travel', 'Hotel', 'Food']
    sizes = [transport, hotel, food]
    colors = ['#3185FC', '#2EC4B6', '#FF3366']

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')

    # Save the pie chart to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    return base64.b64encode(img.getvalue()).decode('utf8')
