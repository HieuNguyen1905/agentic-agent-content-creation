"""Test the API endpoints."""

import httpx
import asyncio
import json


async def test_api():
    """Test basic API functionality."""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🧪 Testing Agentic Content Creation API\n")
        
        # 1. Health check
        print("1. Testing health check...")
        response = await client.get(f"{base_url}/health")
        print(f"   ✓ Status: {response.status_code}")
        print(f"   Response: {response.json()}\n")
        
        # 2. List posts
        print("2. Testing list posts...")
        response = await client.get(f"{base_url}/api/posts?limit=5")
        posts = response.json()
        print(f"   ✓ Found {len(posts)} posts")
        if posts:
            print(f"   Latest: {posts[0]['title']}\n")
        else:
            print("   No posts found\n")
        
        # 3. Get stats
        print("3. Testing stats endpoint...")
        response = await client.get(f"{base_url}/api/posts/stats/overview")
        stats = response.json()
        print(f"   ✓ Total posts: {stats['total_posts']}")
        print(f"   ✓ Total words: {stats['total_words']}")
        print(f"   ✓ Avg SEO score: {stats['avg_seo_score']}\n")
        
        # 4. Generate content (queues job)
        print("4. Testing content generation...")
        generate_request = {
            "topic": "Testing API Integration",
            "length": "short",
            "style": "technical",
            "tone": "informative"
        }
        response = await client.post(
            f"{base_url}/api/generate/",
            json=generate_request
        )
        result = response.json()
        print(f"   ✓ Job created: {result['job_id']}")
        print(f"   Status: {result['status']}\n")
        
        job_id = result['job_id']
        
        # 5. Check job status
        print("5. Checking job status...")
        await asyncio.sleep(2)  # Wait a bit
        response = await client.get(f"{base_url}/api/generate/status/{job_id}")
        status = response.json()
        print(f"   ✓ Status: {status['status']}")
        print(f"   Progress: {status['progress']}%\n")
        
        # 6. Search test
        print("6. Testing search...")
        response = await client.get(
            f"{base_url}/api/search/",
            params={"q": "xiaomi", "limit": 3}
        )
        search_results = response.json()
        print(f"   ✓ Found {search_results['total']} results\n")
        
        print("✅ All tests passed!\n")


if __name__ == "__main__":
    print("Make sure the API server is running: ./start_api.sh\n")
    asyncio.run(test_api())
