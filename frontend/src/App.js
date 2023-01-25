import { Routes, Route } from "react-router-dom";

import Navigation from "./routes/navigation/navigation.route";
import Home from "./routes/home/home.route";
import About from "./routes/about/about.route";
import NotFound from "./routes/not-found/not-found.route";


const App = () => {
  return (
    <Routes>
      <Route path="/" element={<Navigation />}>
        <Route path="/" element={<Home />} />
        <Route path="about" element={<About />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}

export default App;
