import axiosInstance from "@/lib/axios";
import type { User } from "@/types";
import axios from "axios";
import { toast } from "sonner";
import { create } from "zustand";
interface UserStore {
  user: User | null;
  setUser: (user: User) => void;
  getCurrentUser: () => Promise<void>;
  login: (email:string,password:string) => Promise<void>;
  logout: () => void;
}
const useUserStore = create<UserStore>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  getCurrentUser: async () => {
    try {
      const response = await axiosInstance.post(
        "/auth/verify-token",
        {
          token: sessionStorage.getItem("authToken"),
        },
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      if (response.data.valid) {
        set({ user: response.data.data });
      }
    } catch (error: any) {
      console.log("Error while getting current user: ", error.message);
    }
  },
  login: async (email,password) => {
    
    try {
      const response = await axios.post("http://localhost:8001/login", {
        username:email,
        password
      });
      if (response.status === 200) {
        sessionStorage.setItem("authToken", response.data.access_token);
        set({ user: response.data.user });
        toast.success("Login successful!");
      }
    } catch (error: any) {
      console.log("Error while logging in: ", error.message);
      toast.error("Login failed: " + error.message);
    }
  },
  logout: () => {
    sessionStorage.removeItem("authToken");
    set({ user: null });
  },
}));

export default useUserStore;
