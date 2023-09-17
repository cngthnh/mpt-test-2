
class IndexedDBWrapper {

    constructor(dbName, dbVersion, onUpgradeNeeded) {
        this._db = null;
        this._dbName = dbName;
        this._dbVersion = dbVersion;

        // check if onUpgradeNeeded is a function and not null
        if (onUpgradeNeeded && typeof onUpgradeNeeded === "function") {
            this._onUpgradeNeeded = onUpgradeNeeded;
        } 
    }

    _openDb()  {
        return new Promise((resolve, reject) => {
            const dBOpenRequest  = indexedDB.open(this._dbName, this._dbVersion);

            dBOpenRequest.onerror = (event) => {
                reject(event);
            };

            dBOpenRequest.onsuccess = (event) => {
                this._db = dBOpenRequest.result;
                resolve(event);
            };

            dBOpenRequest.onupgradeneeded = (event)=>{
                this._onUpgradeNeeded(event);

                this._db = dBOpenRequest.result;
            }
        });
    }

    _close() {
        this._db.close();
    }

    add(dbStoreName, items) {
        return new Promise((resolve, reject) => {
            this._openDb()
                .then(() => {
                    const transaction = this._db.transaction(
                        [dbStoreName],
                        "readwrite"
                    );

                    const objectStore = transaction.objectStore(
                        dbStoreName
                    );

                    // add items to the object store
                    items.forEach((item) => {
                        objectStore.add(item);
                    });

                    transaction.oncomplete = (event) => {
                        this._close();
                        resolve(event);
                    };

                    transaction.onerror = (event) => {
                        this._close();
                        reject(event);
                    }
                })
                .catch((error) => {
                    reject(error);
                });
        });
    }

    getStoreSize(dbStoreName) {
        return new Promise((resolve, reject) => {
            this._openDb()
                .then(() => {
                    const transaction = this._db.transaction(
                        [dbStoreName],
                        "readonly"
                    );
                    const objectStore = transaction.objectStore(
                        dbStoreName
                    );
                    const request = objectStore.getAll();

                    request.onerror = (event) => {
                        this._close();
                        reject(event);
                    };

                    request.onsuccess = (event) => {
                        const result = event.target.result;
                        this._close();
                        resolve(result.length);
                    };
                })
                .catch((error) => {
                    reject(error);
                });
        });
    }

    popAll(dbStoreName) {
        return new Promise((resolve, reject) => {
            this._openDb()
                .then(() => {
                    const transaction = this._db.transaction(
                        [dbStoreName],
                        "readwrite"
                    );
                    const objectStore = transaction.objectStore(
                        dbStoreName
                    );
                    const request = objectStore.getAll();

                    request.onerror = (event) => {
                        this._close();
                        reject(event);
                    };

                    request.onsuccess = (event) => {
                        const result = event.target.result;

                        // clear the object store
                        const clearRequest = objectStore.clear();

                        clearRequest.onerror = (event) => {
                            reject(event);
                        };

                        clearRequest.onsuccess = (event) => {
                            transaction.oncomplete = (event) => {
                                this._close();
                                resolve(result);
                            };

                            transaction.onerror = (event) => {
                                this._close();
                                reject(event);
                            };
                        };
                    };
                })
                .catch((error) => {
                    reject(error);
                });
        });
    }

    pop(dbStoreName, num) {
        return new Promise((resolve, reject) => {
            this._openDb()
                .then(() => {
                    const transaction = this._db.transaction(
                        [dbStoreName],
                        "readwrite"
                    );
                    const objectStore = transaction.objectStore(
                        dbStoreName
                    );
                    const request = objectStore.getAll();

                    request.onerror = (event) => {
                        this._close();
                        reject(event);
                    };

                    request.onsuccess = (event) => {
                        const result = event.target.result;
                        const items = result.slice(-num);
                        const remainingItems = result.slice(0, -num);

                        // clear the object store
                        const clearRequest = objectStore.clear();

                        clearRequest.onerror = (event) => {
                            reject(event);
                        };

                        clearRequest.onsuccess = (event) => {
                            // add remaining items to the object store
                            remainingItems.forEach((item) => {
                                objectStore.add(item);
                            });

                            transaction.oncomplete = (event) => {
                                this._close();
                                resolve(items);
                            };

                            transaction.onerror = (event) => {
                                this._close();
                                reject(event);
                            };
                        };
                    };
                })
                .catch((error) => {
                    reject(error);
                });
        });
    }
}

export default IndexedDBWrapper;

