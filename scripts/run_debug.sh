echo "--- GAMIT ---"
docker cp debug_auth.py app_gamit:/app/
docker exec app_gamit python debug_auth.py

echo "--- SUPLAY ---"
docker cp debug_auth.py app_store:/app/
docker exec app_store python debug_auth.py

echo "--- LIPAD ---"
docker cp debug_auth.py app_gfa:/app/
docker exec app_gfa python debug_auth.py
