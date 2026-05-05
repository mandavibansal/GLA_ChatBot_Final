from supermemory import Supermemory
import dotenv

dotenv.load_dotenv()
client = Supermemory()

# Add a memory
# client.add(
#     content="User prefers dark mode",
#     container_tags=["user-123"],
# )

# Search memories
results = client.search.documents(
    q="Placements",
   
)
print(results)