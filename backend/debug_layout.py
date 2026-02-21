import asyncio
import logging
import sys
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock settings if needed or rely on env
os.environ["GROQ_API_KEY"] = "gsk_..." # It should be in env or .env, but I'll assume it's loaded from app.core.config if available.
# Actually, I'll let app.core.config handle it.

from app.services.layout_generator_service import LayoutGeneratorService

async def main():
    service = LayoutGeneratorService()
    query = "solar energy investment in adrar"
    logger.info(f"Generating layout for: {query}")
    
    try:
        response = await service.generate_layout(query)
        print("\n--- Generated Widgets ---")
        for w in response.widgets:
            print(f"- {w.type}: {w.title}")
            
        # Check if demand widgets are present
        demand_types = ["gauge", "radar", "table", "pie_chart", "map"]
        found = [w.type for w in response.widgets if w.type in demand_types]
        print(f"\nDemand Widgets Found: {found}")
        
    except Exception as e:
        logger.error(f"Top level error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
