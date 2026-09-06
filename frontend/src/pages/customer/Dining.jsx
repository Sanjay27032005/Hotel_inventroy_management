import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { restaurantApi } from "../../api/endpoints";
import { Button, Spinner, EmptyState } from "../../components/ui";

const MOCK_MENU_CATEGORIES = [
  "Starters", "Main Course", "Signature Dishes", "Desserts", "Beverages"
];

const MOCK_MENU = [
  { id: 1, name: "Truffle Lobster Risotto", price: "4500", category: "Signature Dishes", description: "Creamy arborio rice, fresh lobster, infused with black truffle oil and parmesan.", image_url: "https://images.unsplash.com/photo-1559339352-11d035aa65de?q=80&w=800&auto=format&fit=crop" },
  { id: 2, name: "Wagyu Beef Steak", price: "6500", category: "Signature Dishes", description: "Grade A5 Wagyu, perfectly seared, served with garlic herb butter and asparagus.", image_url: "https://images.unsplash.com/photo-1600891964092-4316c288032e?q=80&w=800&auto=format&fit=crop" },
  { id: 3, name: "Saffron Infused Biryani", price: "2200", category: "Main Course", description: "Aromatic basmati rice cooked with tender lamb, saffron, and traditional spices.", image_url: "https://images.unsplash.com/photo-1633945274405-b6c8069047b0?q=80&w=800&auto=format&fit=crop" },
  { id: 4, name: "Gold Leaf Chocolate Tart", price: "1800", category: "Desserts", description: "Rich dark chocolate ganache in a crisp pastry shell, topped with edible 24k gold.", image_url: "https://images.unsplash.com/photo-1511381939415-e44015466834?q=80&w=800&auto=format&fit=crop" },
  { id: 5, name: "Crispy Calamari", price: "1200", category: "Starters", description: "Lightly battered calamari rings served with zesty lemon aioli.", image_url: "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?q=80&w=800&auto=format&fit=crop" },
  { id: 6, name: "Smoked Salmon Crostini", price: "1500", category: "Starters", description: "House-smoked salmon, dill cream cheese, capers on toasted artisan bread.", image_url: "https://images.unsplash.com/photo-1572695157366-5e585ab2b69f?q=80&w=800&auto=format&fit=crop" },
  { id: 7, name: "Pan-Seared Sea Bass", price: "3200", category: "Main Course", description: "Fresh sea bass fillet, lemon butter caper sauce, served over wild rice.", image_url: "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?q=80&w=800&auto=format&fit=crop" },
  { id: 8, name: "Artisanal Cheese Board", price: "4500", category: "Starters", description: "Selection of imported cheeses, honeycomb, candied walnuts, and crackers.", image_url: "https://images.unsplash.com/photo-1482049016688-2d3e1b311543?q=80&w=800&auto=format&fit=crop" },
  { id: 9, name: "CoreStone Signature Cocktail", price: "1200", category: "Beverages", description: "A secretive blend of premium spirits, fresh citrus, and aromatic bitters.", image_url: "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?q=80&w=800&auto=format&fit=crop" },
  { id: 10, name: "Vintage Pinot Noir (Bottle)", price: "8500", category: "Beverages", description: "An elegant, medium-bodied red wine with notes of dark cherry and earth.", image_url: "https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?q=80&w=800&auto=format&fit=crop" },
  { id: 11, name: "Vanilla Bean Panna Cotta", price: "1100", category: "Desserts", description: "Silky Italian custard topped with mixed berry compote.", image_url: "https://images.unsplash.com/photo-1488477181946-6428a0291777?q=80&w=800&auto=format&fit=crop" },
];

export default function Dining() {
  const [menu, setMenu] = useState([]);
  const [categories, setCategories] = useState([]);
  const [activeCategory, setActiveCategory] = useState("Signature Dishes");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    // Fetch menu and categories from backend if possible
    Promise.all([
      restaurantApi.menu().catch(() => ({ data: [] })),
      restaurantApi.categories().catch(() => ({ data: [] }))
    ]).then(([menuRes, catRes]) => {
      const fetchedMenu = menuRes.data.length ? menuRes.data : MOCK_MENU;
      const fetchedCats = catRes.data.length ? catRes.data.map(c => c.name) : MOCK_MENU_CATEGORIES;
      
      setMenu(fetchedMenu);
      setCategories(fetchedCats);
      
      // Default to the first category if "Signature Dishes" isn't present
      if (!fetchedCats.includes("Signature Dishes") && fetchedCats.length > 0) {
        setActiveCategory(fetchedCats[0]);
      }
    }).finally(() => {
      setLoading(false);
    });
  }, []);

  const displayedMenu = menu.filter(item => 
    !activeCategory || (item.category && item.category.toLowerCase() === activeCategory.toLowerCase())
  );

  return (
    <div className="bg-ink-900 text-linen-50 min-h-screen">
      {/* Hero Section */}
      <section className="relative h-[70vh] flex items-center justify-center overflow-hidden bg-black">
        <div className="absolute inset-0 z-0">
          <img
            src="https://images.unsplash.com/photo-1514933651103-005eec06c04b?q=80&w=2000&auto=format&fit=crop"
            alt="Fine Dining at CoreStone"
            className="h-full w-full object-cover opacity-80 animate-[kenburns_20s_ease-in-out_infinite_alternate]"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-ink-900 via-ink-900/60 to-transparent"></div>
          <div className="absolute inset-0 bg-black/20"></div>
        </div>
        
        <div className="relative z-10 text-center px-4 max-w-4xl mx-auto">
          <p className="text-sm font-bold tracking-[0.3em] text-brass-400 uppercase mb-4 drop-shadow-md">Gastronomy Redefined</p>
          <h1 className="font-display text-5xl sm:text-7xl font-bold tracking-wider text-white uppercase drop-shadow-2xl">
            Fine <span className="text-brass-400 font-light">Dining</span>
          </h1>
          <p className="mt-6 text-lg sm:text-xl text-linen-200/90 leading-relaxed font-light">
            Savor exquisite global flavors curated by our master chefs. Every dish is a masterpiece, crafted with passion and the finest seasonal ingredients.
          </p>
          <Button variant="brass" size="lg" as={Link} to="/book-a-stay" className="mt-10 px-10 py-4 text-sm font-bold uppercase tracking-widest shadow-xl">
            Reserve A Table
          </Button>
        </div>
      </section>

      {/* Menu Section */}
      <section className="py-24 px-6 max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="font-display text-4xl sm:text-5xl font-light uppercase text-white tracking-wide">
            Our <span className="text-brass-500 font-bold">Menu</span>
          </h2>
          <div className="w-24 h-1 bg-brass-500 mx-auto mt-6 rounded-full opacity-50"></div>
        </div>

        {loading ? (
           <div className="flex flex-col items-center justify-center py-20 space-y-4">
             <Spinner className="h-8 w-8 text-brass-500" />
             <p className="text-linen-200/60 font-medium tracking-wider uppercase animate-pulse">Preparing the menu...</p>
           </div>
        ) : (
          <>
            {/* Category Navigation */}
            <div className="flex flex-wrap justify-center gap-2 mb-16">
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setActiveCategory(cat)}
                  className={`px-8 py-3 font-semibold uppercase tracking-widest text-xs transition-all duration-300 rounded-full border ${
                    activeCategory === cat 
                      ? 'bg-brass-500 text-ink-900 border-brass-500 shadow-[0_0_20px_rgba(198,161,91,0.2)]' 
                      : 'border-white/10 text-linen-200/60 hover:text-white hover:border-white/30 hover:bg-white/5'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Menu Items Grid */}
            {displayedMenu.length > 0 ? (
              <div className="grid md:grid-cols-2 gap-x-16 gap-y-12">
                {displayedMenu.map((item, index) => (
                  <div 
                    key={item.id || index} 
                    className="group relative pb-6 border-b border-white/10 transition-all hover:border-brass-500/30 overflow-hidden"
                  >
                    {item.image_url && (
                      <div className="w-full h-48 mb-4 overflow-hidden rounded-xl border border-white/5">
                        <img 
                          src={item.image_url} 
                          alt={item.name}
                          className="w-full h-full object-cover transition-transform duration-[3000ms] group-hover:scale-110"
                        />
                      </div>
                    )}
                    <div className="flex justify-between items-start mb-3">
                      <h3 className="font-display text-2xl text-white group-hover:text-brass-400 transition-colors duration-300 pr-4">
                        {item.name}
                      </h3>
                      <span className="font-display text-xl text-brass-500 shrink-0">
                        ₹{item.price}
                      </span>
                    </div>
                    {item.description && (
                      <p className="text-linen-200/60 leading-relaxed font-light text-sm sm:text-base pr-12">
                        {item.description}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
               <div className="py-20 text-center border border-dashed border-white/10 rounded-2xl bg-white/5">
                 <EmptyState
                   title="Menu Updating"
                   description="Our chefs are currently crafting this section of the menu. Please check back later."
                 />
               </div>
            )}
          </>
        )}
      </section>

      {/* Ambiance/Gallery Preview */}
      <section className="py-20 bg-black">
        <div className="max-w-7xl mx-auto px-6">
           <div className="grid lg:grid-cols-2 gap-12 items-center">
             <div className="order-2 lg:order-1 relative h-[500px] rounded-2xl overflow-hidden shadow-2xl">
                <img 
                  src="https://images.unsplash.com/photo-1559339352-11d035aa65de?q=80&w=1000&auto=format&fit=crop" 
                  alt="Chef's Table" 
                  className="w-full h-full object-cover opacity-80 hover:scale-105 transition-transform duration-1000"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-ink-900 via-transparent to-transparent opacity-80"></div>
             </div>
             <div className="order-1 lg:order-2 lg:pl-12">
                <h2 className="font-display text-4xl sm:text-5xl font-bold uppercase text-white mb-6">
                  An <span className="text-brass-500">Experience</span> Like No Other
                </h2>
                <p className="text-lg text-linen-200/80 leading-relaxed font-light mb-8">
                  Beyond the exquisite flavors, CoreStone Grand offers an atmosphere of unparalleled elegance. Whether you're enjoying an intimate dinner at the Chef's Table or raising a glass at our exclusive lounge, every moment is designed to be unforgettable.
                </p>
                <div className="grid grid-cols-2 gap-8 border-t border-white/10 pt-8">
                   <div>
                      <p className="text-3xl font-display text-brass-500 mb-2">24/7</p>
                      <p className="text-sm font-medium tracking-wider text-linen-200/60 uppercase">In-Room Dining</p>
                   </div>
                   <div>
                      <p className="text-3xl font-display text-brass-500 mb-2">3</p>
                      <p className="text-sm font-medium tracking-wider text-linen-200/60 uppercase">Signature Venues</p>
                   </div>
                </div>
             </div>
           </div>
        </div>
      </section>
    </div>
  );
}
