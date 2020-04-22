"use strict";

const fs = require("fs");
const convert = require("@openapi-contrib/json-schema-to-openapi-schema");

let rawdata = fs.readFileSync("jsonapi-1.0-json-schema.json");
let schema = JSON.parse(rawdata);

(async () => {
  let convertedSchema = await convert(schema);
  let data = JSON.stringify(convertedSchema);
  fs.writeFileSync("jsonapi_oas3.json", data);
})();
