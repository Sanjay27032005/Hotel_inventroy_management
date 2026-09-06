const urls = [
  '1520250497591-112f2f40a3f4',
  '1497361122283-7d2d3c907106',
  '1512918580421-4f11b6bd5ff0',
  '1578683010236-d716f9a3f461',
  '1505691938895-1758d7bef511',
  '1522708323590-d24dbb6b0267',
  '1618773928120-01bb8709e9db',
  '1590490360182-c33d57733427',
  '1560185013-649035134701',
  '1553881651-48245cdce0b5',
  '1514933651103-005eec06c04b',
  '1514362545857-3bc16c4c7d1b',
  '1559339352-11d035aa65de',
  '1517248135467-4c7edcad34c4',
  '1473093295043-cdd812d0e601',
  '1466978913421-bac2e13c11a2',
  '1481833761820-0509d32170b7',
  '1504674900247-0877df9cc836',
  '1464366400600-7168b8af9bc3'
];
async function check() {
  for (let id of urls) {
    try {
      let r = await fetch('https://images.unsplash.com/photo-' + id + '?w=10');
      if (r.status !== 200) console.log(id + ' is BROKEN');
    } catch(e) {
      console.log(id + ' is BROKEN');
    }
  }
  console.log('Done checking');
}
check();
