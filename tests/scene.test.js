import test from 'node:test';
import assert from 'node:assert/strict';
import {spatialModel} from '../src/sceneModel.js';
const data=[{lon:0,lat:0,year:1965},{lon:5,lat:8,year:2000},{lon:10,lat:10,year:2026}];
test('3D spatial encoding keeps positions fixed across filters',()=>{
 const full=spatialModel(data,data),subset=spatialModel([data[1]],data);
 assert.deepEqual(subset.positions[0],full.positions[1]);assert.deepEqual(full.year,[1965,2026]);assert.deepEqual(full.positions[0],[-160,12,145]);assert.deepEqual(full.positions[2],[160,212,-145]);
});
test('3D spatial encoding handles empty selections and singleton domains',()=>{
 assert.deepEqual(spatialModel([],data).positions,[]);assert.ok(spatialModel([data[0]],[data[0]]).positions[0].every(Number.isFinite));
});
