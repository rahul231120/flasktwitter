console.log('Script loaded');
console.log('CSRF Token:', '{{ csrf_token() }}');

function likeTweet(tweetId) {
  console.log('Like button clicked for tweet ID:', tweetId);
  // Simulate the fetch call for testing purposes
  // Replace this with the actual fetch call
  simulateFetch(`/like/${tweetId}`);
}

function retweet(tweetId) {
  console.log('Retweet button clicked for tweet ID:', tweetId);
  // Simulate the fetch call for testing purposes
  // Replace this with the actual fetch call
  simulateFetch(`/retweet/${tweetId}`);
}

function simulateFetch(url) {
  // Simulate a successful response for testing
  const data = { message: 'Simulated success' };
  setTimeout(() => {
    alert(data.message);
    // Optionally, you can update the UI here (e.g., change button color)
  }, 500);
}

document.addEventListener('DOMContentLoaded', function() {
  const buttonsContainer = document.querySelector('.buttons-container');

  if (buttonsContainer) {
    buttonsContainer.addEventListener('click', function(event) {
      const button = event.target;
      const tweetId = button.getAttribute('data-tweet-id');

      if (button.classList.contains('like-button')) {
        likeTweet(tweetId);
      } else if (button.classList.contains('retweet-button')) {
        retweet(tweetId);
      }
    });
  }
});
