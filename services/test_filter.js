
const gamesCache = {
  data: [
    { provider_id: 1, name: 'Game 1', title: 'Title 1' },
    { provider_id: '2', name: 'Game 2', title: 'Title 2' },
    { provider_id: 1, name: 'SearchMe', title: 'Title 3' }
  ]
};

function testFilter(providerId, search) {
  let result = gamesCache.data;
  if (providerId) result = result.filter(g => String(g.provider_id) === String(providerId));
  if (search) result = result.filter(g => (g.name || g.title || '').toLowerCase().includes(search.toLowerCase()));
  return result;
}

console.log('Test 1 (Provider 1):', testFilter(1, null).length); // Should be 2
console.log('Test 2 (Provider "2"):', testFilter('2', null).length); // Should be 1
console.log('Test 3 (Search "Search"):', testFilter(null, 'search').length); // Should be 1
console.log('Test 4 (Provider 1 + Search "Search"):', testFilter(1, 'search').length); // Should be 1
console.log('Test 5 (Search "Title"):', testFilter(null, 'title').length); // Should be 3
