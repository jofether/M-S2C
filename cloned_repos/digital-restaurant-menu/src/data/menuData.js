export const menuData = [
  {
    title: "Appetizers & Starters",
    items: [
      { name: "Truffle Fries", price: "$8.50", desc: "Parmesan, truffle oil, garlic aioli", tags: ["vegetarian", "signature"] },
      { name: "Crispy Calamari", price: "$12.00", desc: "Marinara sauce, lemon wedges, fresh herbs", tags: ["seafood"] },
      { name: "Burrata & Heirloom Tomato", price: "$9.50", desc: "Creamy burrata, balsamic reduction, basil oil", tags: ["vegetarian", "signature"] },
      { name: "Pan-Seared Scallops", price: "$14.00", desc: "Brown butter, microgreens, crispy pancetta", tags: ["seafood", "premium"] },
      { name: "Crispy Duck Confit Leg", price: "$13.50", desc: "Pommes Anna, cherry gastrique", tags: ["premium"] },
      { name: "Grilled Octopus", price: "$11.00", desc: "Chimichurri, fingerling potatoes, charred lemon", tags: ["seafood"] },
    ]
  },
  {
    title: "Soups & Salads",
    items: [
      { name: "Butternut Squash Bisque", price: "$7.50", desc: "Sage brown butter, pumpkin seed oil, crème fraîche", tags: ["vegetarian", "seasonal"] },
      { name: "French Onion Soup", price: "$8.00", desc: "Gruyère crust, beef stock, thyme", tags: ["signature"] },
      { name: "Caesar Salad", price: "$9.00", desc: "Romaine, housemade croutons, parmesan, anchovy dressing", tags: ["signature"] },
      { name: "Kale & Quinoa Salad", price: "$10.50", desc: "Pomegranate, toasted almonds, goat cheese, lemon vinaigrette", tags: ["vegetarian", "healthy"] },
      { name: "Burrata Salad with Fresh Vegetables", price: "$11.00", desc: "Mixed greens, heirloom tomatoes, cucumber, burrata, basil oil", tags: ["vegetarian"] },
      { name: "Seared Ahi Tuna Salad", price: "$13.00", desc: "Sesame crust, mixed greens, cucumber, ponzu dressing, avocado", tags: ["seafood"] },
    ]
  },
  {
    title: "Main Courses",
    items: [
      { name: "Grilled Scottish Salmon", price: "$28.00", desc: "Asparagus, mashed potatoes, lemon beurre blanc, dill", tags: ["seafood", "signature"] },
      { name: "Prime Ribeye Steak", price: "$36.00", desc: "12oz USDA Prime, peppercorn sauce, roasted vegetables, fries", tags: ["premium", "signature"] },
      { name: "Pan-Seared Halibut", price: "$26.00", desc: "Cauliflower purée, brown butter, capers, seasonal vegetables", tags: ["seafood"] },
      { name: "Wild Mushroom Risotto", price: "$18.00", desc: "Arborio rice, porcini, truffle oil, parmesan, fresh thyme", tags: ["vegetarian", "signature"] },
      { name: "Duck à l'Orange", price: "$32.00", desc: "Orange gastrique, roasted root vegetables, duck jus", tags: ["premium"] },
      { name: "Herb-Roasted Lamb Shank", price: "$30.00", desc: "Rosemary jus, creamed cauliflower, charred broccolini", tags: ["premium"] },
      { name: "Branzino en Papillote", price: "$25.00", desc: "Steamed in parchment, fennel, white wine, fresh herbs", tags: ["seafood"] },
      { name: "Herb-Crusted Prime Rib", price: "$38.00", desc: "16oz bone-in, au jus, creamed spinach, roasted potatoes", tags: ["premium", "signature"] },
    ]
  },
  {
    title: "Vegetarian Specialties",
    items: [
      { name: "Eggplant Parmigiana", price: "$16.00", desc: "Fried eggplant, marinara, fresh mozzarella, basil", tags: ["vegetarian"] },
      { name: "Vegetable Terrine", price: "$14.00", desc: "Seasonal roasted vegetables, herb coulis, microgreens", tags: ["vegetarian", "vegan-friendly"] },
      { name: "Stuffed Portobello Mushroom", price: "$17.00", desc: "Spinach, ricotta, sun-dried tomato, balsamic reduction", tags: ["vegetarian"] },
      { name: "Quinoa & Vegetable Steak", price: "$15.50", desc: "Beetroot, quinoa, black bean patty, chimichurri", tags: ["vegetarian", "vegan"] },
    ]
  },
  {
    title: "Desserts",
    items: [
      { name: "Chocolate Lava Cake", price: "$7.50", desc: "Molten dark chocolate center, vanilla ice cream, raspberries", tags: ["signature"] },
      { name: "Crème Brûlée", price: "$6.50", desc: "Classic French custard, caramelized sugar, fresh berries", tags: ["signature"] },
      { name: "Tiramisu", price: "$6.00", desc: "Ladyfingers, mascarpone, espresso, cocoa powder", tags: ["signature"] },
      { name: "Panna Cotta", price: "$7.00", desc: "Vanilla panna cotta, passion fruit coulis, honeycomb", tags: ["signature"] },
      { name: "Chocolate Mousse Trio", price: "$8.00", desc: "Dark, milk, and white chocolate mousses", tags: ["premium"] },
      { name: "Lemon Meringue Tart", price: "$6.50", desc: "Pastry cream, lemon curd, toasted meringue", tags: ["signature"] },
      { name: "Strawberry Shortcake", price: "$7.00", desc: "Fluffy cake, fresh whipped cream, seasonal berries", tags: ["seasonal"] },
    ]
  },
  {
    title: "Beverages",
    items: [
      { name: "Espresso", price: "$3.00", desc: "Single or double shot" },
      { name: "Cappuccino", price: "$4.00", desc: "Espresso, steamed milk, foam" },
      { name: "Fresh Lemonade", price: "$3.50", desc: "House-made, seasonal" },
      { name: "Iced Tea", price: "$3.00", desc: "Sweetened or unsweetened" },
      { name: "Freshly Squeezed Orange Juice", price: "$4.00", desc: "Morning specialty" },
      { name: "Mineral Water", price: "$3.00", desc: "Still or sparkling" },
    ]
  },
  {
    title: "Wine Selection",
    items: [
      { name: "Château Margaux 2015", price: "$85.00", desc: "Bordeaux, France - Full-bodied, complex, elegant", tags: ["premium"] },
      { name: "Barolo d'Alba 2016", price: "$65.00", desc: "Piedmont, Italy - Powerful tannins, dark fruits", tags: ["premium"] },
      { name: "Sancerre 2020", price: "$35.00", desc: "Loire Valley, France - Crisp, mineral, fruity" },
      { name: "Chianti Classico Riserva 2017", price: "$45.00", desc: "Tuscany, Italy - Cherry, violet, earthy notes" },
      { name: "Sauvignon Blanc 2021", price: "$32.00", desc: "New Zealand - Fresh, tropical, herbaceous" },
      { name: "Pinot Noir 2019", price: "$40.00", desc: "California - Silky, red cherry, oak" },
      { name: "Prosecco", price: "$28.00", desc: "Veneto, Italy - Light, festive, crisp" },
      { name: "House Red", price: "$25.00", desc: "By the glass or bottle" },
      { name: "House White", price: "$24.00", desc: "By the glass or bottle" },
    ]
  },
];
