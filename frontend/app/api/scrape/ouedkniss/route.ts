import { NextRequest, NextResponse } from "next/server";

// ==============================================
// Ouedkniss GraphQL Scraper API Route
// ==============================================
// Proxies search queries to Ouedkniss's GraphQL API
// and returns structured product listing data.

const OUEDKNISS_GRAPHQL = "https://api.ouedkniss.com/graphql";

const SEARCH_QUERY = `
  query Search($q: String, $filter: SearchFilterInput) {
    search(q: $q, filter: $filter) {
      announcements {
        data {
          id
          title
          slug
          description
          pricePreview
          priceUnit
          oldPrice
          defaultMedia {
            mediaUrl
          }
          mediaCount
          cities {
            id
            name
            slug
          }
          store {
            id
            name
            slug
          }
        }
        paginatorInfo {
          lastPage
          total
        }
      }
    }
  }
`;

interface OuedknissResult {
    id: string;
    title: string;
    price: number | null;
    priceUnit: string;
    oldPrice: number | null;
    imageUrl: string | null;
    url: string;
    location: string;
    description: string;
    store: string | null;
    totalResults: number;
}

export async function GET(request: NextRequest) {
    const searchParams = request.nextUrl.searchParams;
    const query = searchParams.get("q");
    const page = parseInt(searchParams.get("page") || "1", 10);
    const count = parseInt(searchParams.get("count") || "12", 10);

    if (!query || query.trim().length === 0) {
        return NextResponse.json(
            { error: "Search query 'q' is required" },
            { status: 400 }
        );
    }

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000);

        const response = await fetch(OUEDKNISS_GRAPHQL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "User-Agent":
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                Accept: "application/json",
                Origin: "https://www.ouedkniss.com",
                Referer: "https://www.ouedkniss.com/",
            },
            body: JSON.stringify({
                query: SEARCH_QUERY,
                variables: {
                    q: query.trim(),
                    filter: {
                        count,
                        page,
                    },
                },
            }),
            signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            console.error(
                `Ouedkniss API returned ${response.status}: ${response.statusText}`
            );
            return NextResponse.json(
                { error: "Failed to fetch from Ouedkniss", results: [] },
                { status: 502 }
            );
        }

        const data = await response.json();

        if (data.errors) {
            console.error("Ouedkniss GraphQL errors:", data.errors);
            return NextResponse.json(
                { error: "Ouedkniss API returned errors", results: [] },
                { status: 502 }
            );
        }

        const announcements = data?.data?.search?.announcements;
        if (!announcements?.data) {
            return NextResponse.json({ results: [], total: 0 });
        }

        const total = announcements.paginatorInfo?.total || 0;

        const results: OuedknissResult[] = announcements.data.map(
            (item: Record<string, unknown>) => {
                const cities = item.cities as Array<{ name: string }> | null;
                const store = item.store as { name: string; slug: string } | null;
                const defaultMedia = item.defaultMedia as { mediaUrl: string } | null;

                return {
                    id: item.id,
                    title: item.title || "Untitled",
                    price: item.pricePreview || null,
                    priceUnit: item.priceUnit || "DA",
                    oldPrice: item.oldPrice || null,
                    imageUrl: defaultMedia?.mediaUrl || null,
                    url: `https://www.ouedkniss.com/${item.slug}`,
                    location: cities?.map((c) => c.name).join(", ") || "",
                    description: ((item.description as string) || "").slice(0, 200),
                    store: store?.name || null,
                    totalResults: total,
                };
            }
        );

        return NextResponse.json({
            results,
            total,
            page,
            lastPage: announcements.paginatorInfo?.lastPage || 1,
        });
    } catch (error) {
        if (error instanceof Error && error.name === "AbortError") {
            return NextResponse.json(
                { error: "Request to Ouedkniss timed out", results: [] },
                { status: 504 }
            );
        }

        console.error("Ouedkniss scraper error:", error);
        return NextResponse.json(
            { error: "Internal server error", results: [] },
            { status: 500 }
        );
    }
}
