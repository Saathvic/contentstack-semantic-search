import axios from "axios";
import { useEffect } from "react";

const stackApiKey = "bltaec246e239ee5b66";
const deliveryToken = "cs9bc546f25d43cfbc9312632d";
const environment = "production";
const contentType = "product"; // replace with the actual UID

const url = `https://eu-cdn.contentstack.com/v3/content_types/${contentType}/entries?environment=${environment}`;

function FetchContentstackEntries() {
  useEffect(() => {
    axios.get(url, {
      headers: {
        api_key: stackApiKey,
        access_token: deliveryToken,
      }
    }).then(res => {
      console.log(res.data.entries);
    }).catch(err => {
      console.error(err);
    });
  }, []);

  return <div>Check console for Contentstack entries.</div>;
}

export default FetchContentstackEntries;
