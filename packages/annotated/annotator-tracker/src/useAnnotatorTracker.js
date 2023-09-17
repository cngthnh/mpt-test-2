import React from "react";
import IndexedDBWrapper from "./indexed-db-wrapper";
const DB_NAME = "annotator.tracker";
const DB_STORE_NAME = "annotator.tracker";

export function pythonTime() {
  return Date.now() / 1000;
}

const useAnnotatorTracker = function (
  handleMetadataSubmit,
  isLoading,
  logRate = 5000
) {
  const db = new IndexedDBWrapper(DB_NAME, 1, (event) => {
      const objectStore = event.target.result.createObjectStore(DB_STORE_NAME, {
          keyPath: "id",
          autoIncrement:true
      });
      objectStore.createIndex("timestamp", "timestamp", {
          unique: false,
      });
      objectStore.createIndex("userId", "userId", { unique: false });
      objectStore.createIndex("type", "type", { unique: false });
      objectStore.createIndex("data", "data", { unique: false });
  });

  const handleBehaviorsSubmit = React.useCallback(
    (behaviors) => {
      handleMetadataSubmit({
        type: "behaviors",
        data: [...behaviors],
      });
    },
    [handleMetadataSubmit]
  );

  const cacheBehaviors = React.useCallback((type, action) => {
    const behavior = {
      ...action,
      type,
      time: pythonTime(),
    };

    db.add(DB_STORE_NAME, [behavior]);

  }, []);

  const addListener = React.useCallback((targets, action, handler) => {
    targets.forEach((target) => {
      target.addEventListener(action, handler);
    });
    return () => {
      targets.forEach((target) => {
        target.removeEventListener(action, handler);
      });
    };
  }, []);

  React.useEffect(() => {
    fetch("https://api.ipify.org?format=json", {}).then((response) => {
      response.json().then((data) => {
        cacheBehaviors("ipinfo", data);
      });
    });

    cacheBehaviors("screen_size", {
      screen_width: window.screen.width,
      screen_height: window.screen.height,
      window_width: window.innerWidth,
      window_height: window.innerHeight,
    });

    const handleMouseClick = (event) => {
      cacheBehaviors("window_click", {
        event_x: event.pageX,
        event_y: event.pageY,
      });
    };
    window.addEventListener("click", handleMouseClick);

    function debounce(fn, delay) {
      let timer = null;
      return function () {
        let context = this;
        let args = arguments;
        clearTimeout(timer);
        timer = setTimeout(function () {
          fn.apply(context, args);
        }, delay);
      };
    } 

    const scrollHandler = debounce(function(){
            cacheBehaviors("window_scroll", {
                        scroll_x: window.scrollX,
                        scroll_y: window.scrollY,
            });
    }, 1000);
    const handleMouseScroll = (e)=>{ scrollHandler() };
    window.addEventListener("scroll", handleMouseScroll);

    const handleVisibilityChange = () => {
      cacheBehaviors("window_visibility", {
        visibility_state: document.visibilityState,
      });
    };
    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      window.removeEventListener("click", handleMouseClick);
      window.removeEventListener("scroll", handleMouseScroll);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [cacheBehaviors]);

  React.useLayoutEffect(() => {
        const removeAllFocusListeners = addListener(
      Array.from(document.getElementsByTagName("*")),
      "focus",
      (event) => {
        cacheBehaviors("all_focus", {
          element_tag: event.target.tagName,
          element_name: event.target.name,
          element_id: event.target.id,
          outerHtml: event.target.outerHTML,
        });
      }
    );

    const removeSelectChangeListeners = addListener(
      Array.from(document.getElementsByTagName("select")),
      "change",
      (event) => {
        cacheBehaviors("select_change", {
          outerHtml: event.target.outerHTML,
          element_tag: event.target.tagName,
          element_name: event.target.name,
          element_id: event.target.id,
          input_type: "select",
          value: event.target.value,
        });
      }
    );

    const removeButtonClickListeners = addListener(
      Array.from(document.getElementsByTagName("button")),
      "click",
      (event) => {
        cacheBehaviors("button_click", {
          outerHtml: event.target.outerHTML,
          button: event.target.innerText,
        });
      }
    );

    let prevKey = 0;
    const removeInputClickListeners = addListener(
      [
        ...Array.from(document.getElementsByTagName("input")),
        ...Array.from(document.getElementsByTagName("textarea")),
      ],
      "click",
      (event) => {
        cacheBehaviors("input_click", {
          outerHtml: event.target.outerHTML,
          element_tag: event.target.tagName,
          element_name: event.target.name,
          element_id: event.target.id,
          input_type: event.target.type.toLowerCase(),
          value: event.target.value,
        });
        prevKey = 0;
      }
    );

    const removeInputKeyUpListeners = addListener(
      [
        ...Array.from(document.getElementsByTagName("input")),
        ...Array.from(document.getElementsByTagName("textarea")),
      ],
      "keyup",
      (event) => {
        const specialKey = [0, 8, 13, 37, 38, 39, 40, 46];
        // click, enter, backspace, left, up, right, down, delete
        const currentKey = event.keyCode;
        if (
          (!specialKey.includes(currentKey) && specialKey.includes(prevKey)) ||
          (specialKey.includes(currentKey) && currentKey !== prevKey)
        ) {
          cacheBehaviors("input_keyup", {
            outerHtml: event.target.outerHTML,
            element_tag: event.target.tagName,
            element_name: event.target.name,
            element_id: event.target.id,
            input_type: event.target.type.toLowerCase(),
            cursor_position: event.target.selectionStart,
            value: event.target.value,
          });
        }
        prevKey = event.keyCode;
      }
    );

    const removeInputBlurListeners = addListener(
      [
        ...Array.from(document.getElementsByTagName("input")).filter(
          (input) => input.type === "text"
        ),
        ...Array.from(document.getElementsByTagName("textarea")),
      ],
      "blur",
      (event) => {
        cacheBehaviors("input_blur", {
          outerHtml: event.target.outerHTML,
          element_tag: event.target.tagName,
          element_name: event.target.name,
          element_id: event.target.id,
          input_type: event.target.type.toLowerCase(),
          cursor_position: event.target.selectionStart,
          value: event.target.value,
        });
      }
    );

    const removeInputPasteListeners = addListener(
      [
        ...Array.from(document.getElementsByTagName("input")).filter(
          (input) => input.type === "text"
        ),
        ...Array.from(document.getElementsByTagName("textarea")),
      ],
      "paste",
      (event) => {
        cacheBehaviors("input_paste", {
          outerHtml: event.target.outerHTML,
          element_tag: event.target.tagName,
          element_name: event.target.name,
          element_id: event.target.id,
          input_type: event.target.type.toLowerCase(),
          cursor_position: event.target.selectionStart,
          value: event.clipboardData.getData("text"),
        });
      }
    );

    const removeInputCutListeners = addListener(
      [
        ...Array.from(document.getElementsByTagName("input")).filter(
          (input) => input.type === "text"
        ),
        ...Array.from(document.getElementsByTagName("textarea")),
      ],
      "cut",
      (event) => {
        const startPos = event.target.selectionStart;
        const endPos = event.target.selectionEnd;
        cacheBehaviors("input_cut", {
          outerHtml: event.target.outerHTML,
          element_tag: event.target.tagName,
          element_name: event.target.name,
          element_id: event.target.id,
          input_type: event.target.type.toLowerCase(),
          cursor_position: event.target.selectionStart,
          value: event.target.value.substring(startPos, endPos),
        });
      }
    );

    const removeInputCopyListeners = addListener(
      [
        ...Array.from(document.getElementsByTagName("input")).filter(
          (input) => input.type === "text"
        ),
        ...Array.from(document.getElementsByTagName("textarea")),
      ],
      "copy",
      (event) => {
        const startPos = event.target.selectionStart;
        const endPos = event.target.selectionEnd;
        cacheBehaviors("input_copy", {
          element_tag: event.target.tagName,
          element_name: event.target.name,
          element_id: event.target.id,
          input_type: event.target.type.toLowerCase(),
          cursor_position: event.target.selectionStart,
          value: event.target.value.substring(startPos, endPos),
        });
      }
    );

    const sendBehavior = () => {
      if (isLoading) {
        return;
      }
      db.popAll(DB_STORE_NAME).then((behaviors) => {
        if (behaviors.length > 0) {
          handleBehaviorsSubmit(behaviors);
        }
      });
    };

    window.addEventListener("beforeunload", sendBehavior);

    const timer = setInterval(sendBehavior, logRate);

    return () => {
      removeAllFocusListeners();
      removeSelectChangeListeners();
      removeButtonClickListeners();
      removeInputClickListeners();
      removeInputKeyUpListeners();
      removeInputBlurListeners();
      removeInputPasteListeners();
      removeInputCutListeners();
      removeInputCopyListeners();
      window.removeEventListener("beforeunload", sendBehavior);
      clearInterval(timer);
    };
  }, [handleBehaviorsSubmit, isLoading, cacheBehaviors, addListener]);

  return {
    cacheBehaviors,
  };
};

export default useAnnotatorTracker;
