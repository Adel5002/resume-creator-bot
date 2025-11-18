const telegram  = () => {
    if (window.Telegram && window.Telegram.WebApp) {
      const tele = window.Telegram.WebApp;
      tele.ready();
      return tele;
    }
}

export default telegram