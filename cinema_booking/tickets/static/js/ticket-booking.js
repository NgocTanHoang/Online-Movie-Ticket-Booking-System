$(document).ready(function () {
    var currentGfgStep, nextGfgStep, previousGfgStep;
    var opacity;
    var current = 1;
    var steps = $("fieldset").length;

    // Function to update progress bar
    function setProgressBar(currentStep) {
        var percent = parseFloat(100 / steps) * currentStep;
        percent = percent.toFixed();
        $(".progress-bar").css("width", percent + "%");
    }

    // Function to update Continue Booking button state
    function updateContinueButton() {
        if (current === 1) { // Only check for the first step (Showtime Selection)
            const continueButton = document.getElementById('screen-next-btn');
            const selectedShowtimeId = window.selectedShowtimeId; // Access global variable
            continueButton.disabled = !selectedShowtimeId;
        }
    }

    // Initialize progress bar and button state
    setProgressBar(current);
    updateContinueButton();

    // Handle next step
    $(".next-step").click(function () {
        if ($(this).prop("disabled")) {
            return; // Prevent proceeding if button is disabled
        }

        currentGfgStep = $(this).closest('fieldset');
        nextGfgStep = currentGfgStep.next('fieldset');
        if (!nextGfgStep.length) {
            console.error('Next fieldset not found');
            return;
        }

        $("#progressbar li").eq($("fieldset").index(nextGfgStep))
            .removeClass("not_active")
            .addClass("active");

        nextGfgStep.show();
        currentGfgStep.animate({
            opacity: 0
        }, {
            step: function (now) {
                opacity = 1 - now;
                currentGfgStep.css({
                    'display': 'none',
                    'position': 'relative'
                });
                nextGfgStep.css({
                    'opacity': opacity
                });
            },
            duration: 500
        });
        setProgressBar(++current);
        updateContinueButton(); // Update button state for the new step
    });

    // Handle previous step
    $(".previous-step").click(function () {
        currentGfgStep = $(this).closest('fieldset');
        previousGfgStep = currentGfgStep.prev('fieldset');
        if (!previousGfgStep.length) {
            console.error('Previous fieldset not found');
            return;
        }

        $("#progressbar li").eq($("fieldset").index(currentGfgStep))
            .removeClass("active")
            .addClass("not_active");

        previousGfgStep.show();
        currentGfgStep.animate({
            opacity: 0
        }, {
            step: function (now) {
                opacity = 1 - now;
                currentGfgStep.css({
                    'display': 'none',
                    'position': 'relative'
                });
                previousGfgStep.css({
                    'opacity': opacity
                });
            },
            duration: 500
        });
        setProgressBar(--current);
        updateContinueButton(); // Update button state when going back
    });

    // Prevent form submission on submit button (if any)
    $(".submit").click(function () {
        return false;
    });
});