// --- DOM Elements ---
// Navigation & Main Screens
const containerOne = document.querySelector('.container-one');
const writeBtn = document.querySelector('#write-BTN');
const seeBtn = document.querySelector('#seeBtn');
const postDiv = document.querySelector('#posts');
const backBtn = document.querySelector('#go-back');

// Auth Screens & Elements
const authWind = document.querySelector('.Auth-wind');
const authFormContainer = document.querySelector('.auth-form');
const authForm = document.querySelector('#id-form');
const loginTab = document.querySelector('#login');
const registerTab = document.querySelector('#register');

// Auth Inputs & Buttons
const confirmPassGroup = document.querySelectorAll('.auth-form .input-group')[2]; // 3rd input group
const authSubmitBtn = document.querySelector('.auth-form button[type="submit"]');
const authCancelBtn = document.querySelector('.auth-form button[type="button"]');

// Blog Form Elements
const blogFormContainer = document.querySelector('.form');
const blogForm = document.querySelector('#qu');
const titleInput = document.querySelector('#title');
const blogInput = document.querySelector('#blog');
const blogCancelBtn = document.querySelector('#cancelBtn');

// --- State Variables ---
const API_URL = 'https://my-boilerplate-production.up.railway.app';
const telegramWebApp = window.Telegram?.WebApp;
const miniAppInitData = telegramWebApp?.initData || '';
let isLoggedIn = Boolean(miniAppInitData);
let isRegisterMode = false;
const postsStatus = document.querySelector('#posts-status');

// --- Utility Functions ---

// Hides all views to avoid layout overlap
function hideAllViews() {
  containerOne.classList.add('hidden');
  authWind.classList.add('hidden');
  authFormContainer.classList.add('hidden');
  blogFormContainer.classList.add('hidden');
  postDiv.classList.add('hidden');
}

function apiHeaders() {
  return {
    'Content-Type': 'application/json',
    Authorization: `TelegramMiniApp ${miniAppInitData}`,
  };
}

// Renders a single post card inside #posts
function createPostElement(id, title, content) {
  const newPost = document.createElement('article');
  newPost.className = 'post-card';
  const titleElement = document.createElement('h2');
  const contentElement = document.createElement('p');
  const deleteButton = document.createElement('button');
  titleElement.textContent = title;
  contentElement.textContent = content;
  deleteButton.type = 'button';
  deleteButton.textContent = 'Delete';
  deleteButton.dataset.diaryId = id;
  deleteButton.addEventListener('click', () => deletePost(id));
  newPost.append(titleElement, contentElement, deleteButton);
  postDiv.appendChild(newPost);
}

async function loadPosts() {
  if (!miniAppInitData) {
    postsStatus.textContent = 'Open this page inside Telegram to load your diaries.';
    return;
  }

  try {
    const response = await fetch(`${API_URL}/miniapp/diaries/`, {
      headers: apiHeaders(),
    });
    if (!response.ok) throw new Error('Unable to load diaries.');

    postDiv.querySelectorAll('.post-card').forEach((post) => post.remove());
    const diaries = await response.json();
    if (!diaries.length) {
      postsStatus.textContent = 'No diary entries yet.';
      return;
    }
    postsStatus.textContent = '';
    diaries.forEach((diary) => createPostElement(diary.id, diary.title, diary.content));
  } catch (error) {
    postsStatus.textContent = error.message;
  }
}

async function deletePost(id) {
  if (!confirm('Delete this diary entry?')) return;

  try {
    const response = await fetch(`${API_URL}/miniapp/diaries/${id}`, {
      method: 'DELETE',
      headers: apiHeaders(),
    });
    if (!response.ok) throw new Error('The diary entry could not be deleted.');
    await loadPosts();
  } catch (error) {
    alert(error.message);
  }
}

// Initial Mini App setup
telegramWebApp?.ready();
telegramWebApp?.expand();

// --- Auth Tab Switching Logic ---

loginTab.addEventListener('click', () => {
  isRegisterMode = false;
  loginTab.classList.add('active');
  registerTab.classList.remove('active');
  confirmPassGroup.classList.add('hidden');
  authSubmitBtn.textContent = 'Sign in';
});

registerTab.addEventListener('click', () => {
  isRegisterMode = true;
  registerTab.classList.add('active');
  loginTab.classList.remove('active');
  confirmPassGroup.classList.remove('hidden');
  authSubmitBtn.textContent = 'Register Account';
});

// --- Main Navigation Listeners ---

// "Write New Blog" Click
writeBtn.addEventListener('click', () => {
  hideAllViews();
  if (!isLoggedIn) {
    // Prompt auth windows if user isn't logged in
    authWind.classList.remove('hidden');
    authFormContainer.classList.remove('hidden');
  } else {
    // Open blog creation form directly
    blogFormContainer.classList.remove('hidden');
  }
});

// Auth Form Submission is unnecessary inside a Telegram Mini App.
authForm.addEventListener('submit', (e) => {
  e.preventDefault();
  alert('Authentication is handled by Telegram Mini App.');
});

// Auth Cancel Button
authCancelBtn.addEventListener('click', () => {
  hideAllViews();
  containerOne.classList.remove('hidden');
});

// Blog Form Submission (Creating a Post)
blogForm.addEventListener('submit', (e) => {
  e.preventDefault();

  const titleValue = titleInput.value.trim();
  const blogValue = blogInput.value.trim();

  if (!titleValue || !blogValue) {
    alert('Please fill out both the title and content!');
    return;
  }

  if (!miniAppInitData) {
    alert('Open this page inside Telegram to save diary entries.');
    return;
  }

  fetch(`${API_URL}/miniapp/diaries/`, {
    method: 'POST',
    headers: apiHeaders(),
    body: JSON.stringify({ title: titleValue, content: blogValue }),
  }).then(async (response) => {
    if (!response.ok) throw new Error('The diary entry could not be saved.');
    blogForm.reset();
    hideAllViews();
    containerOne.classList.remove('hidden');
    await loadPosts();
  }).catch((error) => alert(error.message));

});

// Blog Form Cancel Button
blogCancelBtn.addEventListener('click', () => {
  hideAllViews();
  containerOne.classList.remove('hidden');
});

// "See Old Blogs" Click
seeBtn.addEventListener('click', () => {
  hideAllViews();
  postDiv.classList.remove('hidden');
  loadPosts();
});

// "Go Back" Click
backBtn.addEventListener('click', () => {
  hideAllViews();
  containerOne.classList.remove('hidden');
});