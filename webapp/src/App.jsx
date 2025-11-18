import { useState } from 'react'
import MainPage from "./pages/mainPage"
import telegram from './api/telegramApi'

const App = () => {
  const user = telegram()?.initDataUnsafe?.user ?? { username: '', photo_url: '' }
  console.log(user.photo_url)
  return <MainPage username={user.username} avatarUrl={user.photo_url} />
}

export default App