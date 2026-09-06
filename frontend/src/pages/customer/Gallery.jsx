import { useEffect, useState } from "react";
import { galleryApi } from "../../api/endpoints";
import { EmptyState, Spinner } from "../../components/ui";

const CATEGORIES = [
  { key: "", label: "All" },
  { key: "hotel", label: "Exterior & Lobby" },
  { key: "rooms", label: "Suites & Rooms" },
  { key: "restaurant", label: "Dining" },
  { key: "party_hall", label: "Events" },
  { key: "pool", label: "Aquatic Center" },
  { key: "spa", label: "Wellness" },
];

const MOCK_GALLERY = [
  // Exterior & Lobby (hotel)
  { id: 1, category: "hotel", title: "Grand Entrance", image_url: "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?q=80&w=1200&auto=format&fit=crop" },
  { id: 2, category: "hotel", title: "Luxury Facade", image_url: "https://images.unsplash.com/photo-1519225421980-715cb0215aed?q=80&w=1200&auto=format&fit=crop" },
  { id: 3, category: "hotel", title: "Evening Architecture", image_url: "https://images.unsplash.com/photo-1505373877841-8d25f7d46678?q=80&w=1200&auto=format&fit=crop" },
  
  // Suites & Rooms (rooms)
  { id: 4, category: "rooms", title: "Presidential Suite", image_url: "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?q=80&w=1200&auto=format&fit=crop" },
  { id: 5, category: "rooms", title: "Premium Suite", image_url: "https://images.unsplash.com/photo-1519046904884-53103b34b206?q=80&w=1200&auto=format&fit=crop" },
  { id: 6, category: "rooms", title: "Executive Suite", image_url: "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?q=80&w=1200&auto=format&fit=crop" },
  
  // Dining (restaurant)
  { id: 7, category: "restaurant", title: "Wagyu Steak", image_url: "https://images.unsplash.com/photo-1600891964092-4316c288032e?q=80&w=1200&auto=format&fit=crop" },
  { id: 8, category: "restaurant", title: "Signature Cocktails", image_url: "https://images.unsplash.com/photo-1590490360182-c33d57733427?q=80&w=1200&auto=format&fit=crop" },
  { id: 9, category: "restaurant", title: "Fine Indian Cuisine", image_url: "https://images.unsplash.com/photo-1633945274405-b6c8069047b0?q=80&w=1200&auto=format&fit=crop" },
  
  // Events (party_hall)
  { id: 10, category: "party_hall", title: "Gala Setup", image_url: "https://images.unsplash.com/photo-1499856871958-5b9627545d1a?q=80&w=1200&auto=format&fit=crop" },
  { id: 11, category: "party_hall", title: "Wedding Setup", image_url: "https://images.unsplash.com/photo-1514933651103-005eec06c04b?q=80&w=1200&auto=format&fit=crop" },
  { id: 12, category: "party_hall", title: "Conference Layout", image_url: "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?q=80&w=1200&auto=format&fit=crop" },
  
  // Aquatic Center (pool)
  { id: 13, category: "pool", title: "Infinity Pool", image_url: "https://images.unsplash.com/photo-1559339352-11d035aa65de?q=80&w=1200&auto=format&fit=crop" },
  { id: 14, category: "pool", title: "Rooftop Pool", image_url: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=1200&auto=format&fit=crop" },
  { id: 15, category: "pool", title: "Indoor Heated Pool", image_url: "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?q=80&w=1200&auto=format&fit=crop" },
  
  // Wellness (spa)
  { id: 16, category: "spa", title: "Tranquil Spa", image_url: "https://images.unsplash.com/photo-1518684079-3c830dcef090?q=80&w=1200&auto=format&fit=crop" },
  { id: 17, category: "spa", title: "Massage Therapy", image_url: "https://images.unsplash.com/photo-1564501049412-61c2a3083791?q=80&w=1200&auto=format&fit=crop" },
  { id: 18, category: "spa", title: "Relaxation Area", image_url: "https://images.unsplash.com/photo-1504674900247-0877df9cc836?q=80&w=1200&auto=format&fit=crop" },
];

export default function Gallery() {
  const [active, setActive] = useState("");
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    galleryApi
      .list(active || undefined)
      .then((res) => {
        setImages(res.data.length ? res.data : MOCK_GALLERY.filter(img => !active || img.category === active));
      })
      .catch(() => {
        setImages(MOCK_GALLERY.filter(img => !active || img.category === active));
      })
      .finally(() => setLoading(false));
  }, [active]);

  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden bg-ink-900 text-linen-50">
        <div className="absolute inset-0 z-0 overflow-hidden">
          <img
            src="https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?q=80&w=1200&auto=format&fit=crop"
            alt="Gallery"
            className="h-full w-full object-cover opacity-90 animate-[kenburns_20s_ease-in-out_infinite_alternate]"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-ink-900 via-ink-900/40 to-transparent"></div>
          <div className="absolute inset-0 bg-black/10"></div>
        </div>
        <div className="relative z-10 mx-auto max-w-4xl px-6 py-24 text-center lg:py-32">
          <h1 className="font-display text-5xl font-light text-linen-50 sm:text-6xl md:text-7xl">
            Visual <span className="font-medium text-brass-400">Journey</span>
          </h1>
          <p className="mt-6 text-lg text-linen-200/80 leading-relaxed max-w-2xl mx-auto">
            Step inside CoreStone Grand. Browse our curated gallery to glimpse the luxury, elegance, and meticulous attention to detail that awaits you.
          </p>
        </div>
      </section>

      <div className="bg-linen-50 py-12">
        <div className="mx-auto max-w-7xl px-6">
          <div className="flex flex-wrap items-center justify-center gap-3">
            {CATEGORIES.map((cat) => (
              <button
                key={cat.key}
                onClick={() => setActive(cat.key)}
                className={`rounded-full px-6 py-2.5 text-sm font-medium transition-all duration-300 ${
                  active === cat.key 
                    ? "bg-ink-900 text-linen-50 shadow-md shadow-ink-900/20 scale-105" 
                    : "bg-white text-ink-700/70 border border-ink-700/10 hover:bg-brass-50 hover:text-brass-800 hover:border-brass-200"
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-6 py-16">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 space-y-4">
            <Spinner className="h-8 w-8 text-brass-500" />
            <p className="text-ink-700/60 animate-pulse">Loading gallery...</p>
          </div>
        ) : images.length === 0 ? (
          <div className="py-12">
            <EmptyState
              title="Curation in Progress"
              description="Our team is updating this collection. Please explore another category or check back soon."
            />
          </div>
        ) : (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {images.map((img) => (
              <figure key={img.id} className="group relative overflow-hidden rounded-2xl bg-linen-200 shadow-sm transition-shadow hover:shadow-xl">
                <div className="aspect-[4/3] w-full">
                  <img 
                    src={img.image_url} 
                    alt={img.title || img.category} 
                    className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110" 
                  />
                </div>
                {/* Gradient overlay on hover */}
                <div className="absolute inset-0 bg-gradient-to-t from-ink-900/90 via-ink-900/20 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
                
                {/* Caption that slides up */}
                <figcaption className="absolute inset-x-0 bottom-0 translate-y-4 p-6 opacity-0 transition-all duration-300 group-hover:translate-y-0 group-hover:opacity-100">
                   {img.title && <p className="font-display text-xl text-white">{img.title}</p>}
                   <p className="mt-1 text-sm font-medium tracking-wider text-brass-400 uppercase">{img.category}</p>
                </figcaption>
              </figure>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
