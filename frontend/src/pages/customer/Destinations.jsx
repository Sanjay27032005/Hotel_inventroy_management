import { Link } from "react-router-dom";
import { Button } from "../../components/ui";

const DESTINATIONS = [
  {
    id: "paris",
    name: "CoreStone Paris",
    location: "Paris, France",
    description: "Experience the romance and elegance of the French capital from our historic city-center chateau. Featuring Michelin-starred dining and views of the Eiffel Tower.",
    image: "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=1200&auto=format&fit=crop"
  },
  {
    id: "maldives",
    name: "CoreStone Maldives",
    location: "Malé Atoll, Maldives",
    description: "A tranquil escape featuring overwater villas, crystal clear lagoons, and pristine white sands. Your ultimate private island sanctuary.",
    image: "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=1200&auto=format&fit=crop"
  },
  {
    id: "dubai",
    name: "CoreStone Dubai",
    location: "Dubai, UAE",
    description: "Unmatched luxury in the heart of the desert metropolis. Sky-high suites, exclusive shopping access, and breathtaking panoramic city views.",
    image: "https://images.unsplash.com/photo-1542314831-c6a4d27160c1?q=80&w=1200&auto=format&fit=crop"
  },
  {
    id: "swiss-alps",
    name: "CoreStone Swiss Alps",
    location: "Zermatt, Switzerland",
    description: "A winter wonderland retreat offering exclusive ski-in/ski-out access, heated infinity pools, and unparalleled alpine serenity.",
    image: "https://images.unsplash.com/photo-1571896349842-33c89424de2d?q=80&w=1200&auto=format&fit=crop"
  }
];

export default function Destinations() {
  return (
    <div className="bg-ink-900 min-h-screen font-sans">
      {/* Hero Section */}
      <section className="relative h-[60vh] overflow-hidden flex items-center justify-center bg-black">
        <div className="absolute inset-0 z-0 overflow-hidden">
          <img
            src="https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?q=80&w=1200&auto=format&fit=crop"
            alt="Global Destinations"
            className="h-full w-full object-cover opacity-90 animate-[kenburns_25s_ease-in-out_infinite_alternate]"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-ink-900 via-transparent to-transparent"></div>
          <div className="absolute inset-0 bg-black/10"></div>
        </div>
        <div className="relative z-10 mx-auto max-w-4xl px-6 text-center mt-16">
          <h1 className="font-display text-5xl font-bold text-white sm:text-6xl md:text-7xl uppercase tracking-widest drop-shadow-2xl">
            Our <span className="text-brass-400">Destinations</span>
          </h1>
          <p className="mt-6 text-lg text-linen-100/90 leading-relaxed max-w-2xl mx-auto drop-shadow-md">
            Explore our curated collection of luxury properties across the globe. Find your perfect escape, from tranquil resorts to vibrant city-center hotels.
          </p>
        </div>
      </section>

      {/* Destinations Showcase Grid */}
      <section className="mx-auto max-w-7xl px-6 py-20 lg:py-32">
        <div className="grid gap-12 lg:gap-24">
          {DESTINATIONS.map((dest, index) => (
            <div 
              key={dest.id} 
              className={`flex flex-col lg:flex-row items-center gap-8 lg:gap-16 ${index % 2 !== 0 ? 'lg:flex-row-reverse' : ''}`}
            >
              {/* Image Container with Hover Ken Burns Effect */}
              <div className="w-full lg:w-1/2 relative group overflow-hidden rounded-2xl shadow-2xl aspect-[4/3] bg-black">
                 <img 
                   src={dest.image} 
                   alt={dest.name} 
                   className="h-full w-full object-cover transition-transform duration-[10000ms] group-hover:scale-125"
                 />
                 <div className="absolute inset-0 bg-gradient-to-t from-ink-900/60 via-transparent to-transparent opacity-40 group-hover:opacity-10 transition-opacity duration-700"></div>
              </div>

              {/* Text Content */}
              <div className="w-full lg:w-1/2 text-left">
                <div className="inline-flex items-center space-x-2 rounded-full border border-brass-500/30 bg-brass-500/10 px-3 py-1 text-xs text-brass-400 backdrop-blur-sm mb-4">
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                  <span className="uppercase tracking-widest">{dest.location}</span>
                </div>
                <h2 className="font-display text-4xl sm:text-5xl font-bold uppercase text-white mb-6">
                  {dest.name}
                </h2>
                <p className="text-lg text-linen-200/80 leading-relaxed mb-8">
                  {dest.description}
                </p>
                <div className="flex gap-4">
                  <Button variant="brass" as={Link} to="/book-a-stay" className="px-8 py-3 text-sm font-bold uppercase tracking-widest shadow-lg shadow-brass-500/20">
                    Book This Property
                  </Button>
                  <Button variant="outline" as={Link} to="/gallery" className="px-8 py-3 text-sm font-bold uppercase tracking-widest border-white/20 text-white hover:bg-white hover:text-ink-900">
                    View Gallery
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Global Promise Section */}
      <section className="bg-[#162723] py-24 text-center border-t border-white/5">
        <div className="mx-auto max-w-3xl px-6">
           <h2 className="font-display text-3xl sm:text-4xl font-bold text-white uppercase tracking-wider mb-6">The CoreStone Promise</h2>
           <p className="text-lg text-linen-200/70 leading-relaxed mb-10">
             No matter which destination you choose, the CoreStone standard of uncompromising luxury, personalized service, and architectural brilliance remains exactly the same.
           </p>
           <Button variant="brass" as={Link} to="/book-a-stay" className="px-12 py-4 shadow-xl">
             PLAN YOUR JOURNEY
           </Button>
        </div>
      </section>

    </div>
  );
}
