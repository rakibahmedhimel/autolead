from app.services.social_finder import find_social_links


website = "https://www.ljhconstruction.ca/"

result = find_social_links(
    website
)

print(result)