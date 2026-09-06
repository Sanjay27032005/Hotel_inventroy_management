import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "../../components/ui";

const STORIES = [
  {
    id: 1,
    title: "The Ultimate Guide to Maldivian Sunsets",
    tagline: "Destination Guides",
    content: "Discover the best spots across our private islands to catch the breathtaking Maldivian sunsets, complete with bespoke cocktail pairings and uninterrupted views of the Indian Ocean.",
    image: "https://images.unsplash.com/photo-1519823551278-64ac92734fb1?q=80&w=1200&auto=format&fit=crop"
  },
  {
    id: 2,
    title: "A Culinary Journey Through Paris",
    tagline: "Gastronomy",
    content: "Join our Michelin-starred executive chef on a tour of the finest local markets in Paris, and see how fresh ingredients are transformed into our signature dining experiences.",
    image: "https://images.unsplash.com/photo-1544161515-4ab6ce6db874?q=80&w=1200&auto=format&fit=crop"
  },
  {
    id: 3,
    title: "Finding Zen in the Swiss Alps",
    tagline: "Wellness & Spa",
    content: "Explore the holistic benefits of high-altitude wellness. Our alpine spa therapists share the secrets of combining traditional hot stone therapies with crisp mountain air.",
    image: "https://images.unsplash.com/photo-1522798514-97ceb8c4f1c8?q=80&w=1200&auto=format&fit=crop"
  },
  {
    id: 4,
    title: "Dubai Skyline: A Masterclass in Architecture",
    tagline: "Culture & Design",
    content: "Take a deep dive into the architectural marvels that surround CoreStone Dubai. A curated guide for design enthusiasts looking to explore the desert metropolis.",
    image: "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?q=80&w=1200&auto=format&fit=crop"
  }
];

export default function More() {
  const [subscribed, setSubscribed] = useState(false);
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");

  const handleSubscribe = () => {
    if (!email.trim()) {
      setError("Email address is required.");
      return;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      setError("Please enter a valid email address.");
      return;
    }
    setError("");
    setSubscribed(true);
  };

  return (
    <div className="bg-ink-900 min-h-screen font-sans">
      {/* Hero Section */}
      <section className="relative h-[60vh] overflow-hidden flex items-center justify-center bg-black">
        <div className="absolute inset-0 z-0 overflow-hidden">
          <img
            src="https://images.unsplash.com/photo-1544148103-0773bf10d330?q=80&w=1200&auto=format&fit=crop"
            alt="Travel Journal"
            className="h-full w-full object-cover opacity-90 animate-[kenburns_25s_ease-in-out_infinite_alternate]"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-ink-900 via-transparent to-transparent"></div>
          <div className="absolute inset-0 bg-black/30"></div>
        </div>
        <div className="relative z-10 mx-auto max-w-4xl px-6 text-center mt-16">
          <h1 className="font-display text-5xl font-bold text-white sm:text-6xl md:text-7xl uppercase tracking-widest drop-shadow-2xl">
            The <span className="text-brass-400">Journal</span>
          </h1>
          <p className="mt-6 text-lg text-white drop-shadow-lg leading-relaxed max-w-2xl mx-auto font-medium">
            Immerse yourself in our world. Destination guides, local attractions, and holiday recommendations curated by the CoreStone team.
          </p>
        </div>
      </section>

      {/* Stories Grid */}
      <section className="mx-auto max-w-7xl px-6 py-20 lg:py-32">
        <div className="grid gap-10 sm:grid-cols-2">
          {STORIES.map((story) => (
            <article key={story.id} className="group flex flex-col overflow-hidden rounded-2xl bg-[#162723] border border-white/10 shadow-2xl transition-all hover:-translate-y-2 hover:border-brass-500/50 hover:shadow-brass-900/20">
              <div className="aspect-[16/9] w-full overflow-hidden bg-black">
                <img 
                  src={story.image} 
                  alt={story.title} 
                  className="h-full w-full object-cover opacity-90 transition-transform duration-700 group-hover:scale-105"
                />
              </div>
              <div className="flex flex-1 flex-col p-8">
                <span className="text-xs font-bold uppercase tracking-widest text-brass-400 mb-3">{story.tagline}</span>
                <h2 className="font-display text-2xl font-bold text-white mb-4 group-hover:text-brass-400 transition-colors">{story.title}</h2>
                <p className="text-linen-200/80 leading-relaxed mb-8 flex-1">
                  {story.content}
                </p>
                <div className="mt-auto">
                  <Button variant="outline" className="border-brass-500/50 text-brass-400 hover:bg-brass-500 hover:text-ink-900 transition-colors uppercase tracking-widest text-xs font-bold py-2">
                    Read Story
                  </Button>
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>

      {/* Newsletter Signup */}
      <section className="bg-black py-24 text-center border-t border-white/5 relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10 animate-[shimmer_3s_infinite_linear]"></div>
        <div className="mx-auto max-w-3xl px-6 relative z-10">
           <h2 className="font-display text-3xl sm:text-4xl font-bold text-white uppercase tracking-wider mb-6">Stay Inspired</h2>
           
           {subscribed ? (
              <div className="bg-[#162723] border border-brass-500/30 rounded-xl p-8 max-w-lg mx-auto animate-in fade-in zoom-in duration-500">
                <h3 className="text-brass-400 font-display text-2xl mb-2">Welcome to the Club</h3>
                <p className="text-linen-200/80">You're on the list. Keep an eye on your inbox for our latest stories and exclusive offers.</p>
              </div>
           ) : (
              <>
                <p className="text-lg text-linen-200/70 leading-relaxed mb-10">
                  Subscribe to our newsletter to receive the latest travel stories, exclusive offers, and destination guides directly in your inbox.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center max-w-md mx-auto items-start">
                  <div className="w-full flex-1 text-left">
                    <input 
                      type="email" 
                      value={email}
                      onChange={(e) => {
                        setEmail(e.target.value);
                        setError("");
                      }}
                      placeholder="Your email address" 
                      className={`px-6 py-3 w-full rounded-md bg-white/5 border text-white placeholder:text-white/50 focus:outline-none transition-colors ${
                        error ? "border-red-500/80 focus:border-red-500" : "border-white/20 focus:border-brass-500"
                      }`} 
                    />
                    {error && <p className="text-red-400 text-sm mt-2 ml-1 animate-in fade-in">{error}</p>}
                  </div>
                  <Button variant="brass" onClick={handleSubscribe} className="px-8 py-3 h-[50px] whitespace-nowrap shadow-xl font-bold uppercase tracking-widest">
                    Subscribe
                  </Button>
                </div>
              </>
           )}
        </div>
      </section>

    </div>
  );
}
