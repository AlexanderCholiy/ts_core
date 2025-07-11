const UNIT_MAPPING = {
    0: "bps",
    1: "Kbps", 
    2: "Mbps",
    3: "Gbps",
    4: "Tbps"
};

document.addEventListener('DOMContentLoaded', function() {
    function updateUnitSelects() {
        const unitSelects = document.querySelectorAll('select[name*="unit"]');
        
        unitSelects.forEach(select => {
            const currentValue = select.value;
            
            Array.from(select.options).forEach(option => {
                if (option.value && option.value !== "") {
                    const unitValue = parseInt(option.value);
                    if (UNIT_MAPPING[unitValue]) {
                        option.textContent = UNIT_MAPPING[unitValue];
                    }
                }
            });

            select.value = currentValue;
        });
    }
    
    updateUnitSelects();
    
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                setTimeout(updateUnitSelects, 100);
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});