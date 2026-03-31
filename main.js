const menuItems = [
    {
        id: 'cold-brew',
        name: 'Nitro Cold Brew',
        description: 'Velvety smooth cold brew coffee infused with nitrogen for a rich, creamy head.',
        price: '6.50',
        model: 'https://modelviewer.dev/shared-assets/models/Astronaut.glb', // Placeholder
        img: 'https://images.unsplash.com/photo-1517701604599-bb29b565090c?auto=format&fit=crop&q=80&w=800'
    },
    {
        id: 'burger',
        name: 'Aura Signature Burger',
        description: 'Wagyu beef patty, aged cheddar, truffle aioli, and caramelized onions on a brioche bun.',
        price: '18.00',
        model: 'https://modelviewer.dev/shared-assets/models/Astronaut.glb', // Placeholder
        img: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&q=80&w=800'
    },
    {
        id: 'donut',
        name: 'Glazed Galaxy Donut',
        description: 'Hand-dipped artisan donut with a shimmering vanilla bean glaze.',
        price: '4.75',
        model: 'https://modelviewer.dev/shared-assets/models/Astronaut.glb', // Placeholder
        img: 'https://images.unsplash.com/photo-1527677202312-6cd762696677?auto=format&fit=crop&q=80&w=800'
    },
    {
        id: 'matcha',
        name: 'Ceremonial Matcha',
        description: 'Pure Uji matcha whisked to perfection, served with oat milk and honey.',
        price: '7.00',
        model: 'https://modelviewer.dev/shared-assets/models/Astronaut.glb', // Placeholder
        img: 'https://images.unsplash.com/photo-1515823064-d6e0c04616a7?auto=format&fit=crop&q=80&w=800'
    }
];

const menuGrid = document.getElementById('menuGrid');
const arOverlay = document.getElementById('ar-overlay');
const closeAr = document.getElementById('close-ar');
const viewer = document.getElementById('viewer');
const itemName = document.getElementById('item-name');
const itemDesc = document.getElementById('item-desc');
const itemPrice = document.getElementById('item-price');

function initMenu() {
    if (!menuGrid) return;
    
    menuItems.forEach(item => {
        const card = document.createElement('div');
        card.className = 'menu-card glass';
        card.innerHTML = `
            <div class="card-img">
                <img src="${item.img}" alt="${item.name}">
            </div>
            <div class="card-content">
                <h3>${item.name}</h3>
                <p>${item.description}</p>
            </div>
            <div class="card-footer">
                <span class="price">$${item.price}</span>
                <button class="btn secondary view-ar" data-id="${item.id}">Visualise in AR</button>
            </div>
        `;
        menuGrid.appendChild(card);
    });

    // Event Delegation
    menuGrid.addEventListener('click', (e) => {
        if (e.target.classList.contains('view-ar')) {
            const id = e.target.getAttribute('data-id');
            const item = menuItems.find(i => i.id === id);
            openAR(item);
        }
    });
}

function openAR(item) {
    viewer.src = item.model;
    itemName.textContent = item.name;
    itemDesc.textContent = item.description;
    itemPrice.textContent = `$${item.price}`;
    
    arOverlay.classList.remove('hidden');
    document.body.style.overflow = 'hidden'; // Prevent scroll
}

if (closeAr) {
    closeAr.addEventListener('click', () => {
        arOverlay.classList.add('hidden');
        document.body.style.overflow = 'auto';
    });
}

// Close on outside click
if (arOverlay) {
    arOverlay.addEventListener('click', (e) => {
        if (e.target === arOverlay) {
            arOverlay.classList.add('hidden');
            document.body.style.overflow = 'auto';
        }
    });
}

document.addEventListener('DOMContentLoaded', initMenu);
