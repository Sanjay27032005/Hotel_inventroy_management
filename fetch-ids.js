const categories = ['hotel exterior', 'hotel room', 'fine dining restaurant', 'wedding event hall', 'spa wellness'];

async function fetchIds() {
  for (let cat of categories) {
    try {
      let res = await fetch(`https://unsplash.com/napi/search/photos?query=${encodeURIComponent(cat)}&per_page=5`);
      let data = await res.json();
      console.log(`\n--- ${cat} ---`);
      data.results.forEach(r => console.log(r.id));
    } catch(e) {
      console.log(`Error fetching ${cat}: ${e.message}`);
    }
  }
}

fetchIds();
