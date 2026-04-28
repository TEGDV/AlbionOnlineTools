document.addEventListener('alpine:init', () => {
  Alpine.data('builderManager', (initialComp, id) => ({
    // Builder State
    currentComposition: {
      ...initialComp,
      // Initialize activeSet for each role to track UI state
      roles: initialComp.roles.map(role => ({
        ...role,
        _uid: crypto.randomUUID(),
        activeSet: 'main', // 'main' or index of swap
        swaps: role.swaps || []
      }))
    },
    searchQuery: '',
    compositionID: id,

    // Inventory State
    inventory_items: {},
    inventoryIsLoading: true,
    error: null,
    // Moving Roles Transition helpers
    movingId: null,
    moveDirection: null,
    displacedId: null,
    async init() {
      // Initial fetch (empty query returns full DB via backend cache)
      await this.fetchItems();

      // Watch for search changes to re-fetch
      this.$watch('searchQuery', async (value) => {
        await this.fetchItems(value);
      });
    },

    async fetchItems(query = '') {
      this.inventoryIsLoading = true;
      this.error = null;
      try {
        // Pointing to the cached search endpoint
        const url = `http://127.0.0.1:8000/api/items/search?q=${encodeURIComponent(query.trim())}`;

        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch inventory');

        this.inventory_items = await response.json();
      } catch (err) {
        this.error = "Critical Error: Could not retrieve item databases.";
        console.error(err);
      } finally {
        this.inventoryIsLoading = false;
      }
    },

    handleDragStart(event, item) {
      event.dataTransfer.setData('application/json', JSON.stringify(item));
    },

    dropItem(event, build, slot) {
      const item = JSON.parse(event.dataTransfer.getData('application/json'));
      build[slot] = item;
    },
    getActiveBuild(role) {
      if (role.activeSet === 'main') return role.build;
      return role.swaps[role.activeSet];
    },

    setRoleActiveSet(roleIndex, setIndex) {
      this.currentComposition.roles[roleIndex].activeSet = setIndex;
    },
    addNewRole() {
      this.currentComposition.roles.push({
        name: "New Role",
        build: { weapon: null, off_hand: null, head: null, chest: null, feet: null, cape: null, food: null, potion: null }
      });
    },

    async saveChanges() {
      const response = await fetch(`/party-compositions/${this.compositionID}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.currentComposition)
      });
      if (response.ok) alert("Composition Synchronized.");
    },

    addSwap(role) {
      // 1. Initialize the swaps array if this role doesn't have one yet
      if (!role.swaps) {
        role.swaps = [];
      }

      // 2. Push a clean template into the swaps array
      role.swaps.push({
        weapon: null, 
        off_hand: null, 
        head: null, 
        chest: null, 
        feet: null, 
        cape: null, 
        food: null, 
        potion: null, 
        bag: null
      });

      console.log(`Added new swap. Total swaps for ${role.name}:`, role.swaps.length);
    },

    removeRole(index) {
      if (confirm("Remove this role from the composition?")) {
        this.currentComposition.roles.splice(index, 0);
      }
    },

    moveRoleUp(index) {
      if (index > 0 && !this.movingId) {
        const roles = this.currentComposition.roles;

        // Use the injected _uid
        this.movingId = roles[index]._uid;
        this.displacedId = roles[index - 1]._uid;
        this.moveDirection = 'up';

        setTimeout(() => {
          [roles[index - 1], roles[index]] = [roles[index], roles[index - 1]];
          this.movingId = null;
          this.displacedId = null;
          this.moveDirection = null;
        }, 500);
      }
    },

    moveRoleDown(index) {
      const roles = this.currentComposition.roles;
      if (index < roles.length - 1 && !this.movingId) {
        this.movingId = roles[index]._uid;
        this.displacedId = roles[index + 1]._uid;
        this.moveDirection = 'down';

        setTimeout(() => {
          [roles[index], roles[index + 1]] = [roles[index + 1], roles[index]];
          this.movingId = null;
          this.displacedId = null;
          this.moveDirection = null;
        }, 500);
      }
    },
    async updateBuild() {
      try {
        const response = await fetch(`/party-compositions/${this.compositionID}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.currentComposition)
        });

        if (!response.ok) throw new Error("Failed to update composition.");

        // Optional: Implement a proper UI toast notification here
        alert("Composition updated successfully!");
      } catch (err) {
        console.error("Update error:", err);
        alert("Error updating composition.");
      }
    },

    // NEW: Save as a brand new composition (POST)
    async saveAsNewBuild() {
      try {
        // Create a deep copy and strip the ID to avoid primary key conflicts
        const payload = JSON.parse(JSON.stringify(this.currentComposition));
        delete payload.id; 

        const response = await fetch('/party-compositions/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error("Failed to save as new.");

        const newComp = await response.json();

        // Redirect the user to the newly created composition's edit page
        window.location.href = `/party-compositions/${newComp.id}`;

      } catch (err) {
        console.error("Save as new error:", err);
        alert("Error saving new composition.");
      }
    },
    async deleteBuild() {
      // Force explicit user confirmation before executing destructive actions
      if (!confirm("Are you sure you want to delete this composition? This action cannot be undone.")) {
        return;
      }

      try {
        const response = await fetch(`/party-compositions/${this.compositionID}`, {
          method: 'DELETE'
        });

        if (!response.ok) throw new Error("Failed to delete composition.");

        // Redirect to a safe page to avoid interacting with a deleted record
        window.location.href = '/';

      } catch (err) {
        console.error("Delete error:", err);
        alert("Error deleting composition.");
      }
    },
    async exportImage() {
      this.inventoryIsLoading = true; // Use existing loading state
      try {
        // 1. Internally run update to sync current UI state
        const updateUrl = `/party-compositions/${this.compositionID}`;
        const updateResponse = await fetch(updateUrl, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.currentComposition)
        });

        if (!updateResponse.ok) throw new Error('Failed to synchronize state before export');

        // 2. Run the export endpoint (opens in new tab to trigger download)
        const exportUrl = `/party-compositions/${this.compositionID}/export`;
        window.open(exportUrl, '_blank');

      } catch (err) {
        this.error = "Export Error: " + err.message;
        console.error(err);
      } finally {
        this.inventoryIsLoading = false;
      }
    }
  }));


});
