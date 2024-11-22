import matplotlib.pyplot as plt
import requests

# Constants
REFERER = 'https://results.vertical-life.info/event/110/cr/650'


# ------------------------- Data Retrieval Functions -------------------------

def get_athletes_for_comp(comp_id):
    """Fetch the list of athlete IDs for a given competition."""
    url = f"https://results.vertical-life.info/api/v1/category_rounds/{comp_id}/results"
    response = session.get(url)
    comp_data = response.json()
    return [entry.get("athlete_id") for entry in comp_data.get("ranking", [])]


def get_tops_for(comp_id, athlete_id):
    """Fetch the unique set of 'top' routes for an athlete in a given competition."""
    url = f"https://results.vertical-life.info/api/v1/category_rounds/{comp_id}/athlete_details/{athlete_id}"
    response = requests.get(url, headers={"Referer": REFERER})
    athlete_data = response.json()
    return {ascent['route_name'] for ascent in athlete_data['ascents'] if ascent['top']}


def get_tops_as_list_for(comp_id, athlete_id):
    """create a list indicating the 'top' status for each route in a given competition."""
    topped = [0] * 101
    url = f"https://results.vertical-life.info/api/v1/category_rounds/{comp_id}/athlete_details/{athlete_id}"
    response = session.get(url)
    athlete_data = response.json()
    for ascent in athlete_data['ascents']:
        if ascent['top']:
            topped[int(ascent['route_name'])] = 1
    return topped


def find_athlete_ids_by_name(comp_id, name):
    """Find athlete IDs by matching their name in a given competition."""
    url = f"https://results.vertical-life.info/api/v1/category_rounds/{comp_id}/results"
    response = requests.get(url, headers={"Referer": REFERER})
    comp_data = response.json()
    return [athlete["athlete_id"] for athlete in comp_data.get("ranking", []) if
            name.lower() in athlete["name"].lower()]


# ------------------------- Analysis Functions -------------------------

def get_top_ten(comp_id):
    """Retrieve 'top' data for the top 10 athletes in a competition."""
    participants = get_athletes_for_comp(comp_id)
    return [get_tops_as_list_for(comp_id, athlete_id) for athlete_id in participants[:6]]


def find_decisive_boulders(comp_id):
    """Identify boulders with non-matching results across the top 10 athletes."""
    non_matching_indexes = []
    tops = get_top_ten(comp_id)

    for i in range(len(tops[0])):
        first_value = tops[0][i]
        if not all(sublist[i] == first_value for sublist in tops):
            non_matching_indexes.append(i)

    plot_decisive_boulders(non_matching_indexes, tops)


# ------------------------- Visualization Functions -------------------------

def plot_decisive_boulders(non_matching_indexes, tops):
    """Plot boulders with non-matching values for the top athletes."""
    plt.figure(figsize=(12, 6))

    names = [str(i) for i in non_matching_indexes]
    bottoms = [0] * len(non_matching_indexes)

    for segment in tops:
        segment = [segment[i] for i in non_matching_indexes]
        plt.bar(names, segment, bottom=bottoms)
        bottoms = [x + 1 for x in bottoms]

    plt.xlabel("Boulder")
    plt.xticks(rotation=90)
    plt.gca().get_yaxis().set_visible(False)
    plt.title("Frauen")
    plt.tight_layout()
    plt.savefig("decisive_boulders_f.png")
    plt.show()


def create_num_of_tops_chart(tops_counts, num_of_my_tops):
    """Generate a bar chart of the number of tops."""
    labels = list(range(len(tops_counts)))
    colors = ['red' if label <= num_of_my_tops else 'gray' for label in labels]

    plt.figure(figsize=(12, 6))
    plt.bar(labels, tops_counts, color=colors)
    plt.xlabel('Tops')

    plt.xticks(ticks=labels, rotation=90)
    plt.tight_layout()
    plt.savefig("num_of_tops.png")
    plt.show()


# ------------------------- Main Execution Functions -------------------------


def get_all_tops_for_comp(comp_id):
    athletes = get_athletes_for_comp(comp_id)

    tops = [0] * 101

    for athlete in athletes:
        print(athlete)
        athlete_tops = get_tops_as_list_for(comp_id, athlete)
        for i in range(len(tops)):
            tops[i] += athlete_tops[i]

    return tops

def get_top_counts_for_comp(comp_id):
    athletes = get_athletes_for_comp(comp_id)
    counts = [0] * 101

    for athlete in athletes:
        print(athlete)
        athlete_tops = get_tops_as_list_for(comp_id, athlete)
        count = sum(1 for item in athlete_tops if item != 0)
        counts[count] += 1


    return counts


def compare(athlete1, comp1, athlete2, comp2):
    id1 = find_athlete_ids_by_name(comp1, athlete1)[0]
    id2 = find_athlete_ids_by_name(comp2, athlete2)[0]

    tops1 = get_tops_as_list_for(comp1, id1)
    tops2 = get_tops_as_list_for(comp2, id2)

    different_indices = [i for i, (a, b) in enumerate(zip(tops1, tops2)) if a != b]
    reduced_tops1 = [tops1[i] for i in different_indices]
    reduced_tops2 = [tops2[i] for i in different_indices]

    names = [str(i) for i in different_indices]

    plt.figure(figsize=(12, 6))
    plt.bar(names, reduced_tops1, color='blue')
    plt.bar(names, reduced_tops2, color='red', bottom=1)
    plt.gca().get_yaxis().set_visible(False)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(f"comparison {athlete1} - {athlete2}.png")
    plt.show()


def create_all_tops_stacked_chart():
    my_tops = get_tops_for(649, 1616)
    male_tops = get_all_tops_for_comp(649)
    female_tops = get_all_tops_for_comp(650)
    total_tops = [x + y for x, y in zip(male_tops, female_tops)]

    print({index: value for index, value in enumerate(male_tops)})
    print({index: value for index, value in enumerate(female_tops)})

    print({index: value for index, value in enumerate(total_tops)})

    indexed_tops = list(enumerate(total_tops))
    indexed_tops = [top for top in indexed_tops if top[0] != 0]
    sorted_indexed_tops = sorted(indexed_tops, key=lambda x: x[1], reverse=True)

    names = [str(item[0]) for item in sorted_indexed_tops]
    num_of_tops = [item[1] for item in sorted_indexed_tops]
    colors = ['blue' if label in my_tops else 'gray' for label in names]

    reordered_female_tops = []

    for boulder in sorted_indexed_tops:
        reordered_female_tops.append(female_tops[boulder[0]])

    plt.figure(figsize=(12, 6))
    plt.bar(names, num_of_tops, color=colors)
    plt.bar(names, reordered_female_tops, color='red', zorder=2)
    for i, value in enumerate(num_of_tops):
        plt.text(i, value + 0.5, str(value), ha='center', va='bottom', rotation=90)
    plt.xlabel('Boulder')
    plt.ylabel('Tops')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("tops_per_boulder.png")
    plt.show()

def create_tops_chart(comp_id):
    my_tops = get_tops_for(649, 1616)
    total_tops = get_all_tops_for_comp(comp_id)

    print({index: value for index, value in enumerate(total_tops)})

    indexed_tops = list(enumerate(total_tops))
    indexed_tops = [top for top in indexed_tops if top[0] != 0]
    sorted_indexed_tops = sorted(indexed_tops, key=lambda x: x[1], reverse=True)

    names = [str(item[0]) for item in sorted_indexed_tops]
    num_of_tops = [item[1] for item in sorted_indexed_tops]
    colors = ['blue' if label in my_tops else 'gray' for label in names]


    plt.figure(figsize=(12, 6))
    plt.bar(names, num_of_tops, color=colors)
    for i, value in enumerate(num_of_tops):
        plt.text(i, value + 0.5, str(value), ha='center', va='bottom', rotation=90)
    plt.xlabel('Boulder')
    plt.ylabel('Tops')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(f"tops_per_boulder-{comp_id}.png")
    plt.show()


def get_tops_counts(comp_id):
    top_counts = get_top_counts_for_comp(comp_id)
    print(top_counts)
    create_num_of_tops_chart(top_counts, len(get_tops_for(649, 1616)))

# ------------------------- Example Usage -------------------------

if __name__ == "__main__":
    # find_decisive_boulders(DEFAULT_COMP_ID)
    # analyze_tops_for_all_athletes(DEFAULT_COMP_ID)

    session = requests.Session()
    session.headers.update({"Referer": REFERER})

    #find_decisive_boulders(650)
    #create_all_tops_stacked_chart()
    #create_tops_chart(650)
    #compare('kösling', 649, 'jenny', 650)
    get_tops_counts(650)

    session.close()
