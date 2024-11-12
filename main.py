import requests
import matplotlib.pyplot as plt

# 1616
referer = 'https://results.vertical-life.info/event/110/cr/650'

comp = 649


def get_athletes_for(comp_id):
    url = f"https://results.vertical-life.info/api/v1/category_rounds/{comp_id}/results"
    response = requests.get(url, headers={"Referer": referer})
    comp_data = response.json()
    return [entry.get("athlete_id") for entry in comp_data.get("ranking", [])]


def get_tops_for(comp_id, athlete_id):
    tops = set()
    url = f"https://results.vertical-life.info/api/v1/category_rounds/{comp_id}/athlete_details/{athlete_id}"
    response = requests.get(url, headers={"Referer": referer})
    athlete_data = response.json()
    # Iterate over the ascents to count the 'top' routes
    for ascent in athlete_data['ascents']:
        if ascent['top']:  # Only count routes where 'top' is True
            tops.add(ascent['route_name'])
    return tops


def find_athlete_ids_by_name(name, comp_id):
    url = f"https://results.vertical-life.info/api/v1/category_rounds/{comp_id}/results"
    response = requests.get(url, headers={"Referer": referer})
    comp_data = response.json()

    # Initialize an empty list to store matching athlete IDs
    matching_ids = []

    # Search in the "ranking" section
    for athlete in comp_data.get("ranking", []):
        if name.lower() in athlete["name"].lower():  # Case-insensitive match
            matching_ids.append(athlete["athlete_id"])
    return matching_ids


def find_exclusive_tops(first_id, second_id, comp_id1, comp_id2):
    first_tops = get_tops_for(comp_id1, first_id)
    second_tops = get_tops_for(comp_id2, second_id)

    unique_tops = sorted(map(int, list(set(first_tops) - set(second_tops))))
    print(unique_tops)
    return


def compare(name1, name2):
    id1 = find_athlete_ids_by_name(name1, 649)[0]
    id2 = find_athlete_ids_by_name(name2, 649)[0]
    find_exclusive_tops(id1, id2, 650, 649)


#compare('arnold', 'kösling')

route_counts = {}
top_counts = [0] * 71

my_tops = get_tops_for(649, 1616)

athletes = get_athletes_for(comp)

# Fetch details for each athlete_id
for athlete_id in athletes:

    tops = get_tops_for(comp, athlete_id)

    num_tops = len(tops)

    top_counts[num_tops] += 1

    print(f"Parsing for athlete '{athlete_id}")

    for top in tops:
        if top in route_counts:
            route_counts[top] += 1  # Increment the count for that route name
        else:
            route_counts[top] = 1  # Initialize the count for that route name

# Sort by increasing number of tops
sorted_by_increasing_tops = sorted(route_counts.items(), key=lambda x: x[1])

# Sort by decreasing number of tops
sorted_by_decreasing_tops = sorted(route_counts.items(), key=lambda x: x[1], reverse=True)

# Display sorted results
print("Sorted by increasing number of tops:", sorted_by_increasing_tops)
print("Sorted by decreasing number of tops:", sorted_by_decreasing_tops)
print("my tops:", my_tops)

for boulder in sorted_by_decreasing_tops:
    if boulder[0] not in my_tops:
        print("most tops not by me: ", boulder[0], boulder[1])


def create_tops_per_boulder_chart(sorted_by_decreasing_tops, my_tops):
    # Split data into labels and values
    labels = [item[0] for item in sorted_by_decreasing_tops]
    values = [item[1] for item in sorted_by_decreasing_tops]

    # Define bar colors: red for highlighted keys, gray for others
    colors = ['red' if label in my_tops else 'gray' for label in labels]

    # Create the bar plot
    plt.figure(figsize=(12, 6))
    bars = plt.bar(labels, values, color=colors)

    # Adding labels and title
    plt.xlabel('Boulder', fontsize=12)
    plt.ylabel('Tops', fontsize=12)

    # Rotate x-axis labels for readability
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("/home/sfk/wintercup/tops_per_boulder.png")


def create_num_of_tops_chart(tops_counts, num_of_my_tops):
    # Split data into labels and values
    labels = list(range(len(tops_counts)))
    values = tops_counts

    # Define bar colors: red for highlighted keys, gray for others
    colors = ['red' if label == num_of_my_tops else 'gray' for label in labels]

    # Create the bar plot
    plt.figure(figsize=(12, 6))
    bars = plt.bar(labels, values, color=colors)

    # Adding labels and title
    plt.xlabel('Tops', fontsize=12)
    plt.ylabel('Boulderers', fontsize=12)

    # Rotate x-axis labels for readability
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("/home/sfk/wintercup/num_of_tops.png")


create_tops_per_boulder_chart(sorted_by_decreasing_tops, my_tops)
create_num_of_tops_chart(top_counts, len(my_tops))
